import os

from basic_pitch_inference import basicpitch_inference
from data_mining import data_mining_source, filter
from GPT_Inference import gpt_inference


def rename_files_and_dirs(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        # Check if it is a directory
        if os.path.isdir(file_path):
            # Rename the directory
            new_filename = filename.replace(" ", "_")
            new_file_path = os.path.join(path, new_filename)
            os.rename(file_path, new_file_path)
            # Recursively call the function for the new directory
            rename_files_and_dirs(new_file_path)
        else:
            # Rename the file
            new_filename = filename.replace(" ", "_")
            new_file_path = os.path.join(path, new_filename)
            os.rename(file_path, new_file_path)


def main():
    #channel_table, playlist_table, videos_table = data_mining_source.data_mining()
    rename_files_and_dirs('ground_truth/')
    #print('Transcribing Anime')
    #filter.filter_directories(genre='anime')
    #basicpitch_inference.transcribe_genre_folder(genre='anime', overwrite=True)
    #print('Finished Anime')
    #print('Transcribing kpop')
    #filter.filter_directories(genre='kpop')
    #basicpitch_inference.transcribe_genre_folder(genre='kpop', overwrite=True)
    #print('Finished kpop')
    #print('Transcribing video-game')
    #filter.filter_directories(genre='video-game')
    #basicpitch_inference.transcribe_genre_folder(genre='video-games', overwrite=True)
    #print('Finished video-games')
    gpt_inference.caption_all_genre_folders(overwrite=True)

if __name__ == '__main__':
    main()
