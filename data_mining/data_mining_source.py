import http.client

from googleapiclient.discovery import build
import pandas as pd
import os
from fastprogress.fastprogress import progress_bar
import pytube
from pytube.exceptions import PytubeError
import multiprocessing
import moviepy.editor

from constants import YOUTUBE_API_KEY

from typing import List, Union, Any

GENRE_TAG = 'video-game'


def channel_metadata(url_list: List[str]) -> pd.DataFrame:
    """Returns a DataFrame containing the metadata for each YouTube channel in the input list.

    Includes the channel ID, channel name, and a list of all video URLs. Additionally, returns a list
    of unique channel IDs extracted from the input URLs.

    Args:
        url_list: A list of valid YouTube channel URLs.

    Returns:
        A DataFrame with columns for ChannelID, ChannelName, and AllVideos,
        containing the metadata for each channel in the input list.
        A list of unique channel IDs extracted from the input URLs.
    """
    channel_table = pd.DataFrame(columns=['ChannelID',
                                          'ChannelName',
                                          'AllVideos'])
    channel_ids = []
    channel_names = []
    channel_videos = []
    for url in url_list:
        try:
            channel = pytube.Channel(url)
            channel_ids.append(channel.channel_id)
            channel_names.append(channel.channel_name)
            channel_videos.append(channel.video_urls)
        except:
            # TODO: Move the current URL to somewhere else
            print('BUG WITH: ', url)
            pass

    channel_table['ChannelID'] = channel_ids
    channel_table['ChannelName'] = channel_names
    channel_table['AllVideos'] = channel_videos
    return channel_table


def channel_playlists(youtube: Any, channel_table: pd.DataFrame) -> pd.DataFrame:
    """Retrieves playlist metadata for a list of YouTube channels and adds it to the input channel data.

    Additionally, returns a DataFrame with playlist metadata. The DataFrame contains columns for
    PlaylistID, ChannelID, PlaylistTitle, and PlaylistDescription.

    Args:
        youtube: A YouTube API client instance.
        channel_table: A DataFrame object containing channel metadata for each channel in the input list.

    Returns:
        A DataFrame object with columns for
        PlaylistID, ChannelID, PlaylistTitle, and PlaylistDescription,
        containing the playlist metadata for each channel in the input list.
    """
    playlist_table = pd.DataFrame(columns=['PlaylistID',
                                          'ChannelID',
                                          'PlaylistTitle',
                                          'PlaylistDescription'])

    channel_ids = channel_table['ChannelID'].values.tolist()
    playlist_titles = []
    playlist_descriptions = []
    playlist_ids = []
    channel_ids_new = []

    for channel_id in channel_ids:
        request = youtube.playlists().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50
        )

        response = request.execute()

        for i in range(len(response['items'])):
            playlist_items = response['items'][i]
            channel_id = playlist_items['snippet']['channelId']
            playlist_id = playlist_items['id']

            playlist_ids.append(playlist_id)
            channel_ids_new.append(channel_id)
            playlist_titles.append(playlist_items['snippet']['title'])
            playlist_descriptions.append(playlist_items['snippet']['description'])

    playlist_table['PlaylistID'] = pd.Series(playlist_ids)
    playlist_table['ChannelID'] = pd.Series(channel_ids_new)
    playlist_table['PlaylistTitle'] = pd.Series(playlist_titles)
    playlist_table['PlaylistDescriptions'] = pd.Series(playlist_descriptions)

    return playlist_table


def robust_download(video_url: str) -> List[Union[str, int]]:
    """Downloads the mp4 video file from the input YouTube video URL, converts it to an mp3 audio file and returns
       the video metadata.

    Args:
        video_url: The URL of the YouTube video to download.

    Returns:
        A tuple of two items:
            - A dictionary containing video metadata, including video ID, file path, length, rating, description, and keywords.
            - A list containing video channel ID, video ID, description, length, publish date, and file path.
    """
    try:
        video = pytube.YouTube(video_url)
        video_name = video.title.replace('/', '') + '.mp4'
        audio_name = video.title.replace('/', '') + '.mp3'
        output_path = os.path.join('nerv_dataset', GENRE_TAG, video.title)
        if not os.path.isdir(output_path) and not video.length > 360:
            os.makedirs(output_path)

        if not os.path.isfile(os.path.join(output_path, audio_name)) and not video.length > 360:
            video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc() \
                 .first().download(filename=video_name, output_path=output_path)

            video_editor = moviepy.editor.VideoFileClip(os.path.join(output_path, video_name))
            video_editor.audio.write_audiofile(os.path.join(output_path, audio_name), logger=None)
            os.remove(os.path.join(output_path, video_name))

        row = []
        if not video.length > 360:
            row = [video.video_id, video.channel_id,
                   video.title, video.description,
                   video.length, video.publish_date,
                   video.rating, video.keywords,
                   os.path.join(output_path, audio_name)
            ]

        return row

    except (PytubeError, http.client.IncompleteRead) as e:
        print('Error: ', e)
        return []


def playlist_songs(playlist_table: pd.DataFrame, source_df) -> pd.DataFrame:
    """Extracts song information from playlists and returns a table with song metadata.

    Each playlist in the input playlist table is processed in parallel, with the songs in each playlist being
    extracted and saved to the returned dataframe. The `robust_download` function is used to
    download and convert each song to MP3 format, and the resulting metadata is saved to the returned dataframe.
    Additionally, information about each song is saved to a list of rows,
    which is returned along with the modified dataframe.

    Args:
        playlist_table: A DataFrame containing playlist metadata, including playlist IDs and channel IDs.

    Returns:
        A DataFrame with columns:
        - VideoID: The ID of the YouTube video.
        - ChannelID: The ID of the YouTube channel that uploaded the video.
        - PlaylistID: The ID of the playlist that the video belongs to.
        - Descriptions: The video's description.
        - Length: The video's duration in seconds.
        - PublishedDate: The video's publication date.
        - VideoRating: The video's rating.
        - VideoKeyWords: A list of keywords associated with the video.
        - PathToRaw: The file path to the raw MP3 file.
    """
    data = []
    playlists = playlist_table['PlaylistID'].values.tolist()
    for playlist_id in progress_bar(playlists):
        url = 'https://www.youtube.com/playlist?list={}'.format(playlist_id)
        playlist = pytube.Playlist(url)
        video_urls = playlist.video_urls
        with multiprocessing.Pool(8) as pool:
            for row in pool.map(robust_download, video_urls):
                row.insert(2, playlist.playlist_id)
                data.append(row)

    videos_table = pd.DataFrame(data, columns=[
        'VideoID', 'ChannelID', 'PlaylistID',
        'videoTitle', 'descriptions', 'length', 'publishedDate',
        'videoRating', 'videoKeyWords', 'pathToRaw']
    )

    return videos_table


def data_mining():
    sources_df = pd.read_csv('sources.csv')
    url_list = sources_df['link'].values.tolist()[12:14]
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    channel_table = channel_metadata(url_list)
    channel_table.to_csv('nerv_dataset/channels.csv', index=False)
    playlist_table = channel_playlists(youtube, channel_table)
    playlist_table.to_csv('nerv_dataset/playlists.csv', index=False)
    videos_table = playlist_songs(playlist_table, sources_df)
    videos_table.to_csv('nerv_dataset/videos.csv', index=False)

    return channel_table, playlist_table, videos_table


if __name__ == '__main__':
    data_mining()
