import pandas as pd
import os
import shutil

channels = pd.read_csv('./anime/channels.csv')
playlists = pd.read_csv('./anime/playlists.csv')
videos = pd.read_csv('./anime/videos.csv')

print(len(videos))
videos.head(5)

videos_playlists = videos.merge(playlists, how='left', left_on='playlistID', right_on='PlaylistID')
print(len(videos_playlists))
videos_playlists.head(5)

# %%
videos_playlists.info()

# %%
videos_playlists[videos_playlists['playlistID'].isnull()]

# %% [markdown]
# ## Filtering

# %%
videos_playlists = videos.merge(playlists, how = 'inner', left_on = 'playlistID', right_on = 'PlaylistID')
print(len(videos_playlists))
videos_playlists.head(5)

# %%
videos_playlists['PlaylistTitle'].unique()

# %%
certain_anime = ['studio ghibli', 'anime', 'naruto', 'demon slayer', 'evangelion', "jojo's bizarre", 'kyoani', 'sword art', 'hiroyuki sawano', 'makoto shinkai', 'series', 'attack on titan', 'your lie in april', 'seishun buta yarou']

# %%
certain_index = []
for i in range(len(videos_playlists)):
    playlist_title = videos_playlists.iloc[i]['PlaylistTitle'].lower()
    for keyword in certain_anime:
        if keyword in playlist_title:
            certain_index.append(i)

# %%
print(len(certain_index))
certain_anime_videos = videos_playlists.iloc[certain_index].reset_index()
certain_anime_videos.head(5)

# %%
len(set(certain_anime_videos['videoTitle']))

# %%
file_names = []
for i,x in enumerate(os.listdir('./anime')):
    file_names.append((i,x))
print(len(file_names))
file_names

# %%
i = 0
filtered = []
titles = [i for i in certain_anime_videos['videoTitle']]
for x in file_names:
    if x[1].startswith('.'):
        continue
    if x[1] in titles:
        filtered.append(x)
len(filtered)        

# %%
import shutil
for i,x in enumerate(os.listdir('./anime')):
    if i not in filtered:
        print(x)
        path = './anime/' + str(x)
        shutil.rmtree(path)
print(len(os.listdir('./anime')))        

# %%




# %%
