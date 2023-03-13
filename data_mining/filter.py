import shutil

import pandas as pd
import os

def fetch_filtered_df(genre):
    playlist_df = pd.read_csv(f'./nerv_dataset/{genre}/playlists.csv')
    videos_df = pd.read_csv(f'./nerv_dataset/{genre}/videos.csv')

    merged_df = pd.merge(playlist_df, videos_df, on='PlaylistID')
    keywords = [
        'studio ghibli', 'anime', 'naruto', 'demon slayer',
        'evangelion', "jojo's bizarre", 'kyoani', 'sword art',
        'hiroyuki sawano', 'makoto shinkai', 'series', 'attack on titan',
        'your lie in april', 'seishun buta yarou'
    ]

    keywords = [
        'bts', 'blackpink', '(g)i-dle', 'goblin', 'ateez', 'dreamcatcher', 'big bang', 'eddy kim', 'crush',
        'exo', 'newjeans', 'shinee', 'stray kids', 'tale of the nine tailed', 'txt', 'vixx', 'aespa', 'astro',
        'the sound of magic', 'day6', 'enhypen', 'everglow', 'fromis_9', 'gfriend', 'got7', 'i.o.i', 'ikon',
        'itzy', 'iu', 'ive', 'iz*one', 'jbj', 'jennie', 'somi', 'nct', "nu'est", 'oh my girl',
        'produce x 101', 'treasure', 'twice', 'x1', 'lovelyz', 'red velvet', 'mamamoo', 'melomance', 'momoland',
        'bolbbalgan4', 'block b', 'btob', 'sunmi', 'seventeen', 'sistar', 'snsd', 'april', 'apink',
        'n.flying', 'oh my girl', 'wjsn', 'wanna one', 'loona', 'infinite', 'pentagon', 'produce48', 'highlight', 'heize'
    ]

    keywords = [
        'final fantasy', 'mass effect', 'the whispered world piano', 'horizon zero dawn', 'halo', 'morrowind',
        'bioshock', 'detroit become human', 'trine', 'skyrim', 'witcher', 'wolf\'s rain', 'kirby', 'minecraft',
        'silent hill', 'pokemon', 'Total War', "Battlefront", 'video game', 'game', 'the last of us',
        'republic commando', 'valiant hearts'
    ]

    filtered_df = merged_df[merged_df['PlaylistTitle'].str.contains('|'.join(keywords), case=False)]
    filtered_df = filtered_df[filtered_df['PlaylistID'].notnull()]
    return filtered_df


def filter_directories(genre):
    genre_path = f'./nerv_dataset/{genre}'
    temp_path = f'./nerv_dataset/.{genre}_temp'

    filtered_df = fetch_filtered_df(genre)
    print(len(filtered_df))

    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    folders = [f for f in os.listdir(genre_path) if os.path.isdir(os.path.join(genre_path, f))]
    for folder in folders:
        if folder not in filtered_df['videoTitle'].values.tolist():
            src_path = os.path.join(genre_path, folder)
            dest_path = os.path.join(temp_path, folder)
            shutil.move(src_path, dest_path)
