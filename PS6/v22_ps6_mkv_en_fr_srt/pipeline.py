# pipeline.py
import os
import srt
from datetime import timedelta
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator


# --- Transcription avec progression ---
def transcrire_audio_fast(audio_path, model_size="small", progress_callback=None):
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe(audio_path, beam_size=5)
    segments = list(segments)
    total_segments = len(segments)

    srt_data = []
    for i, segment in enumerate(segments):
        srt_data.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
        if progress_callback:
            percent = int((i + 1) / total_segments * 100)
            progress_callback(percent)
    return srt_data


# --- Convertir en SRT ---
def convertir_en_srt(segments, output_path):
    subs = []
    for i, seg in enumerate(segments):
        start = timedelta(seconds=seg["start"])
        end = timedelta(seconds=seg["end"])
        subs.append(srt.Subtitle(index=i + 1, start=start, end=end, content=seg["text"]))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(subs))


# --- Traduire un SRT avec deep-translator ---
def traduire_srt(input_srt, output_srt, dest_lang="fr", progress_callback=None):
    """
    Traduit chaque ligne du fichier SRT input_srt vers dest_lang et écrit output_srt.
    Appelle progress_callback(percent) si fourni.
    """
    translator = GoogleTranslator(source="auto", target=dest_lang)
    with open(input_srt, "r", encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))

    total = len(subs)
    translated_subs = []

    for i, sub in enumerate(subs):
        try:
            translated_text = translator.translate(sub.content)
        except Exception:
            translated_text = sub.content

        translated_subs.append(
            srt.Subtitle(index=sub.index, start=sub.start, end=sub.end, content=translated_text)
        )

        if progress_callback:
            progress_callback(int((i + 1) / total * 100))

    with open(output_srt, "w", encoding="utf-8") as f:
        f.write(srt.compose(translated_subs))
