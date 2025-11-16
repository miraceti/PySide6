# pipeline.py
import os
import srt
from datetime import timedelta
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
import time

# --- Transcription avec progression ---
def transcrire_audio_fast(audio_path, model_size="small", progress_callback=None):
    """
    Transcrit un fichier audio en texte avec suivi de progression.
    Utilise faster_whisper.
    """
    import wave
    import math
    from faster_whisper import WhisperModel

    # 1️⃣ Calculer la durée totale du fichier audio
    try:
        with wave.open(audio_path, "rb") as f:
            frames = f.getnframes()
            rate = f.getframerate()
            total_duration = frames / float(rate)
    except Exception:
        total_duration = None

    # 2️⃣ Charger le modèle
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    # 3️⃣ Transcrire avec estimation de progression
    segments, info = model.transcribe(audio_path, beam_size=5)
    srt_data = []

    last_percent = -1
    processed_time = 0.0

    for seg in segments:
        srt_data.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        })

        # calcul de progression par rapport au temps écoulé
        processed_time = seg.end
        if total_duration and progress_callback:
            percent = int(min((processed_time / total_duration) * 100, 100))
            if percent != last_percent:
                progress_callback(percent)
                last_percent = percent

    # 4️⃣ Fin — forcer 100 %
    if progress_callback:
        progress_callback(100)

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


# --- Traduire un SRT ---
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
    last_percent = -1

    for i, sub in enumerate(subs):
        try:
            translated_text = translator.translate(sub.content)
        except Exception:
            translated_text = sub.content

        translated_subs.append(
            srt.Subtitle(index=sub.index, start=sub.start, end=sub.end, content=translated_text)
        )

        if progress_callback:
            pct = int((i + 1) / total * 100)
            if pct != last_percent:
                progress_callback(pct)
                last_percent = pct

        # légère pause pour stabilité réseau
        time.sleep(0.1)

    with open(output_srt, "w", encoding="utf-8") as f:
        f.write(srt.compose(translated_subs))

    if progress_callback:
        progress_callback(100)