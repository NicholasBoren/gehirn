import pandas as pd
import os

df = pd.read_csv('musiccaps-public.csv')

ytid_list = [s.split('.')[0] for s in os.listdir('./audio')]

for ytid in ytid_list:
    caption = df.loc[df['ytid'] == ytid]['caption'].tolist()[0]
    with open(f'./text/{ytid}.txt', 'w') as f:
        f.write(caption)