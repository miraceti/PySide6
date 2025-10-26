import whisper
import moviepy as mp
import srt
from datetime import timedelta
from tqdm import tqdm
import os

def extraire_audio(video_path, audio_path="temp_audio.wav"):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    return audio_path

def transcrire_audio(audio_path, model_size="small"):
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result

def convertir_en_srt(segments, output_path="sous_titres.srt"):
    sous_titres = []
    
    for i, seg in tqdm(enumerate(segments), total=len(segments), desc="génération SRT"):
        start =  timedelta(seconds=seg["start"])
        end =  timedelta(seconds=seg["end"])
        content = seg["text"].strip()
        sous_titres.append(srt.Subtitle(index=i+1, start=start, end = end, content =content))
        
    with open(output_path, "w", encoding= "utf-8") as f:
        f.write(srt.compose(sous_titres))
        
def video_vers_srt(video_path):
    audio_path = extraire_audio(video_path)
    transcription = transcrire_audio(audio_path)
    convertir_en_srt(transcription["segments"])
    os.remove(audio_path)
    

video_vers_srt(r'/media/rico/SATURNE/rico/Documents/python/PySide6/PS6/v21_soustitre/CLIP1.mp4')
