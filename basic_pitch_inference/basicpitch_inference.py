import os
import subprocess
import time

DATASET_FOLDER = './nerv_dataset'


def transcribe_all_genre_folders(overwrite=False):
    genre_list = os.listdir(DATASET_FOLDER)
    for genre in genre_list:
        genre_path = os.path.join(DATASET_FOLDER, genre)
        if not genre.startswith('.') and os.path.isdir(genre_path):
            transcribe_genre_folder(genre, overwrite)


def transcribe_genre_folder(genre, overwrite=False):
    '''
    Takes in the name of a genre folder containing .mp3 files and transcribes all songs within
    to .mid

            Parameters:
                    genre (str): the genre whose songs to transcribe
                    overwrite (bool): specify whether transcribing should overwrite existing
                                      .mid files with the same file name
    '''
    genre_path = f'{DATASET_FOLDER}/{genre}'

    song_list = os.listdir(genre_path)

    execution_times = []
    for song_name in song_list:
        if song_name.startswith('.'):
            continue

        mp3_name = song_name + '.mp3'
        midi_name = song_name + '.mid'
        if not overwrite and os.path.isfile(f'{genre_path}/{song_name}/{midi_name}'):
            continue

        song_path = f'{genre_path}/{song_name}'
        if not os.path.exists(song_path):
            os.mkdir(song_path)


        start_time = time.time()
        subprocess.run(['basic-pitch', '{}/{}'.format(genre_path, song_name),
                        '{}/{}/{}'.format(genre_path, song_name, mp3_name)])

        end_time = time.time()
        elapsed_time = end_time - start_time
        execution_times.append(elapsed_time)

    avg_execution_time = sum(execution_times) / len(execution_times)
    print("Genre: {}, Average execution time per song: {:.2f} seconds".format(genre, avg_execution_time))

