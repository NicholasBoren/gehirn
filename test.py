import numpy as np
import librosa
import laion_clap
import torch
import os

torch.cuda.empty_cache()
print()
# quantization
def int16_to_float32(x):
    return (x / 32767.0).astype(np.float32)


def float32_to_int16(x):
    x = np.clip(x, a_min=-1., a_max=1.)
    return (x * 32767.).astype(np.int16)

model = laion_clap.CLAP_Module(enable_fusion=True)
model.load_ckpt()
path = '../../../'

def getFiles(path):
    filenames = []
    audio_files = []
    text_files = []
    for _,_,files in os.walk(path + 'audio', topdown=False):
        filenames.append(files)
    #print(filenames)    
    for name in filenames[0]:
        #print(name)
        n, ext = name.split('.')
        audio_files.append(path + 'audio/' + name)
        text_files.append(path + 'text/' + n +'.txt')
    return audio_files, text_files

audio_files, text_files = getFiles(path)

print(len(audio_files), len(text_files))
print(audio_files[0], text_files[0])

text_data = []
for f in text_files:
    with open(f, 'r') as file:
        data = file.read().replace('\n', '') 
    text_data.append(data)
sims = []
batch_size = 100
for i in range(0, len(audio_files), batch_size): 
    print(i)
    scores = []
    j  = min(i+batch_size, len(audio_files))   
    audio_embed = model.get_audio_embedding_from_filelist(x = audio_files[i:j], use_tensor=True)
    print(audio_embed.shape)
    text_embed = model.get_text_embedding(text_data[i:j], use_tensor=True)
    print(text_embed.shape)

    def compute_similarity(audio_embeddings, text_embeddings):
        r"""Compute similarity between text and audio embeddings"""
        similarity = text_embeddings @ audio_embeddings.T
        return similarity.T

    for i in range(audio_embed.shape[0]):
        scores.append(compute_similarity(audio_embed[i], text_embed[i]))
    print(sum(scores)/len(scores))
    sims.append((sum(scores)/len(scores)))
print(f'Total score: {sum(sims)/len(sims)}')



