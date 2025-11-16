import sys
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QListWidget, QListWidgetItem, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from pipeline import transcrire_audio_fast, convertir_en_srt, traduire_srt

# =====================
# Thread-safe Progress
# =====================
class ProgressEmitter(QObject):
    percent = Signal(int)
    def __init__(self):
        super().__init__()
    def emit(self, v: int):
        self.percent.emit(int(v))

# =====================
# Worker générique
# =====================
class Worker(QThread):
    progress_signal = Signal(str)
    finished_signal = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            class Redirect:
                def __init__(self, signal): self.signal = signal
                def write(self, text):
                    if text.strip():
                        self.signal.emit(text)
                def flush(self): pass

            import sys
            old_stdout = sys.stdout
            sys.stdout = Redirect(self.progress_signal)

            self.func(*self.args, **self.kwargs)

            sys.stdout = old_stdout
            self.finished_signal.emit("✅ Terminé")
        except Exception as e:
            self.finished_signal.emit(f"❌ Erreur : {e}")

# =====================
# Worker FFmpeg
# =====================
class FFmpegWorker(QThread):
    percent_signal = Signal(int)
    finished_signal = Signal(str)

    def __init__(self, command, total_duration):
        super().__init__()
        self.command = command
        self.total_duration = total_duration

    def run(self):
        try:
            proc = subprocess.Popen(self.command, stderr=subprocess.PIPE, universal_newlines=True)
            for line in proc.stderr:
                if "time=" in line:
                    t = line.split("time=")[1].split(" ")[0]
                    h, m, s = t.split(":")
                    cur = int(h) * 3600 + int(m) * 60 + float(s)
                    pct = min(int(cur / self.total_duration * 100), 100)
                    self.percent_signal.emit(pct)
            proc.wait()
            msg = "✅ Terminé" if proc.returncode == 0 else f"❌ Code {proc.returncode}"
            self.finished_signal.emit(msg)
        except Exception as e:
            self.finished_signal.emit(f"❌ {e}")

# =====================
# GUI principale
# =====================
class SubtitleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Générateur MKV multilingue")
        self.setGeometry(200, 200, 850, 650)

        self.video_path = ""
        self.output_dir = ""
        self.audio_path = ""
        self.srt_en = ""
        self.srt_translated = []
        self.mkv_output = ""
        self.video_duration = 1
        self.workers = []

        # Emitters references pour éviter GC
        self._current_transcribe_emitter = None
        self._current_translate_emitter = None

        layout = QVBoxLayout()

        self.btn_select = QPushButton("📁 Sélectionner vidéo")
        self.btn_select.clicked.connect(self.select_video)
        layout.addWidget(self.btn_select)

        self.label_video = QLabel("Aucune vidéo sélectionnée")
        layout.addWidget(self.label_video)

        self.btn_extract = QPushButton("🔊 Extraire audio")
        self.btn_extract.clicked.connect(self.extract_audio)
        layout.addWidget(self.btn_extract)
        self.progress_audio = QProgressBar()
        layout.addWidget(self.progress_audio)

        self.btn_transcribe = QPushButton("🧠 Transcrire audio (anglais)")
        self.btn_transcribe.clicked.connect(self.transcribe_audio)
        layout.addWidget(self.btn_transcribe)
        self.progress_transcribe = QProgressBar()
        layout.addWidget(self.progress_transcribe)

        layout.addWidget(QLabel("Langues cibles :"))
        self.lang_list = QListWidget()
        for lang in ["fr", "es", "de", "it"]:
            item = QListWidgetItem(lang)
            item.setCheckState(Qt.Unchecked)
            self.lang_list.addItem(item)
        layout.addWidget(self.lang_list)

        self.btn_translate = QPushButton("🌐 Traduire SRT")
        self.btn_translate.clicked.connect(self.translate_srt)
        layout.addWidget(self.btn_translate)
        self.progress_translate = QProgressBar()
        layout.addWidget(self.progress_translate)

        self.btn_mkv = QPushButton("🎬 Créer MKV final")
        self.btn_mkv.clicked.connect(self.generate_mkv)
        layout.addWidget(self.btn_mkv)
        self.progress_mkv = QProgressBar()
        layout.addWidget(self.progress_mkv)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    # =====================
    # Étapes
    # =====================
    def select_video(self):
        file, _ = QFileDialog.getOpenFileName(self, "Sélectionner", "", "Videos (*.mp4 *.mkv)")
        if not file:
            return
        self.video_path = file
        base = Path(file).stem
        self.output_dir = os.path.join(Path(file).parent, f"{base}_output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.label_video.setText(f"🎞️ {Path(file).name}")

        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", file]
        try:
            self.video_duration = float(subprocess.check_output(cmd).decode().strip())
        except Exception:
            self.video_duration = 1
        self.log("✅ Vidéo chargée")

    def extract_audio(self):
        if not self.video_path:
            self.log("❌ Aucune vidéo")
            return
        self.audio_path = os.path.join(self.output_dir, "audio.wav")
        cmd = ["ffmpeg", "-y", "-i", self.video_path, "-vn", "-acodec", "pcm_s16le",
               "-ar", "44100", "-ac", "2", self.audio_path]
        self.run_ffmpeg(cmd, self.video_duration, self.progress_audio)
        self.log(source ="Extraction de l'audio ",text="en cours...")

    def transcribe_audio(self):
        if not os.path.exists(self.audio_path):
            self.log("❌ Extraire d'abord l'audio")
            return
        self.srt_en = os.path.join(self.output_dir, Path(self.video_path).stem + "_en.srt")
        self.run_worker(self._transcribe_wrapper)

    def _transcribe_wrapper(self):
        emitter = ProgressEmitter()
        self._current_transcribe_emitter = emitter
        emitter.percent.connect(self.progress_transcribe.setValue)
        self.progress_transcribe.setRange(0, 100)
        self.progress_transcribe.setValue(0)

        self.log("🎧 Transcription de l'audio en cours...")
        transcription = transcrire_audio_fast(self.audio_path, "small", progress_callback=emitter.emit)
        convertir_en_srt(transcription, self.srt_en)

        self.progress_transcribe.setValue(100)
        #self.log("✅ Transcription terminée")
        del self._current_transcribe_emitter

    def translate_srt(self):
        if not os.path.exists(self.srt_en):
            self.log("❌ Pas de fichier SRT anglais")
            return
        langs = [self.lang_list.item(i).text()
                 for i in range(self.lang_list.count())
                 if self.lang_list.item(i).checkState() == Qt.Checked]
        if not langs:
            self.log("❌ Aucune langue sélectionnée")
            return
        for lang in langs:
            srt_out = os.path.join(self.output_dir, Path(self.srt_en).stem + f"_{lang}.srt")
            self.srt_translated.append(srt_out)

            emitter = ProgressEmitter()
            self._current_translate_emitter = emitter
            emitter.percent.connect(self.progress_translate.setValue)

            self.progress_translate.setRange(0, 100)
            self.progress_translate.setValue(0)

            self.run_worker(traduire_srt, self.srt_en, srt_out, lang, progress_callback=emitter.emit)
        self.log("✅ Traduction en cours...")

    def generate_mkv(self):
        if not os.path.exists(self.video_path) or not self.srt_translated:
            self.log("❌ Données manquantes")
            return
        self.mkv_output = os.path.join(self.output_dir, Path(self.video_path).stem + "_final.mkv")
        cmd = ["ffmpeg", "-y", "-i", self.video_path]
        all_srts = [self.srt_en] + self.srt_translated
        for s in all_srts:
            cmd += ["-i", s]
        cmd += ["-map", "0:v", "-map", "0:a"]
        for i in range(1, len(all_srts)+1):
            cmd += ["-map", str(i)]
        cmd += ["-c:v", "copy", "-c:a", "copy", "-c:s", "srt", self.mkv_output]
        self.run_ffmpeg(cmd, self.video_duration, self.progress_mkv)
        self.log("✅ Génération du fichier MKV final terminée")

    # =====================
    # Méthodes génériques
    # =====================
    def run_worker(self, func, *args, **kwargs):
        w = Worker(func, *args, **kwargs)
        self.workers.append(w)
        w.progress_signal.connect(self.log)
        w.finished_signal.connect(lambda msg, ww=w: self.thread_done(ww, msg))
        w.start()

    def run_ffmpeg(self, cmd, duration, bar):
        w = FFmpegWorker(cmd, duration)
        self.workers.append(w)
        w.percent_signal.connect(bar.setValue)
        w.finished_signal.connect(lambda msg, ww=w: self.thread_done(ww, msg))
        bar.setRange(0, 100)
        w.start()

    def thread_done(self, worker, msg, source=""):
        if worker in self.workers:
            self.workers.remove(worker)
        self.log(msg,source="")

    def log(self, text, source=""):
        self.log_area.append(source + text )
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )


# =====================
# MAIN
# =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SubtitleGUI()
    gui.show()
    sys.exit(app.exec())
