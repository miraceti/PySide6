import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QComboBox, QTextEdit, QProgressBar, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path

# --- Import du pipeline ---
from pipeline import (
    extraire_audio_ffmpeg,
    transcrire_audio_fast,
    convertir_en_srt,
    traduire_srt,
    create_mkv_with_multiple_subs
)

# --- Thread pour exécuter une étape ---
class Worker(QThread):
    progress_signal = Signal(str)
    finished_signal = Signal(str)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            class StdOutRedirector:
                def __init__(self, signal):
                    self.signal = signal
                def write(self, text):
                    if text.strip() != "":
                        self.signal.emit(text)
                def flush(self):
                    pass
            import sys
            old_stdout = sys.stdout
            sys.stdout = StdOutRedirector(self.progress_signal)
            self.func(*self.args)
            sys.stdout = old_stdout
            self.finished_signal.emit("✅ Terminé")
        except Exception as e:
            self.finished_signal.emit(f"❌ Erreur : {str(e)}")

# --- Interface GUI améliorée ---
class SubtitleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pipeline Vidéo -> SRT -> MKV")
        self.setGeometry(200, 200, 800, 600)

        self.video_path = ""
        self.output_dir = ""

        layout = QVBoxLayout()

        # --- Sélection vidéo ---
        self.btn_select_video = QPushButton("📁 Sélectionner vidéo")
        self.btn_select_video.clicked.connect(self.select_video)
        layout.addWidget(self.btn_select_video)

        self.label_video = QLabel("Aucune vidéo sélectionnée")
        layout.addWidget(self.label_video)

        # --- Extraction audio ---
        self.btn_extract_audio = QPushButton("🔊 Extraire audio")
        self.btn_extract_audio.clicked.connect(self.extract_audio)
        layout.addWidget(self.btn_extract_audio)

        self.progress_audio = QProgressBar()
        self.progress_audio.setMaximum(0)  # mode indéterminé
        layout.addWidget(self.progress_audio)

        # --- Transcription ---
        self.btn_transcribe = QPushButton("🧠 Transcrire audio (anglais)")
        self.btn_transcribe.clicked.connect(self.transcribe_audio)
        layout.addWidget(self.btn_transcribe)

        self.progress_transcribe = QProgressBar()
        self.progress_transcribe.setMaximum(0)
        layout.addWidget(self.progress_transcribe)

        # --- Choix langues traduction ---
        self.lang_list = QListWidget()
        for lang in ["fr", "es", "de", "it", "pt"]:
            item = QListWidgetItem(lang)
            item.setCheckState(Qt.Unchecked)
            self.lang_list.addItem(item)
        layout.addWidget(QLabel("Langues des sous-titres traduits (sélection multiple) :"))
        layout.addWidget(self.lang_list)

        # --- Bouton traduction ---
        self.btn_translate = QPushButton("🌐 Traduire SRT")
        self.btn_translate.clicked.connect(self.translate_srt)
        layout.addWidget(self.btn_translate)

        self.progress_translate = QProgressBar()
        self.progress_translate.setMaximum(0)
        layout.addWidget(self.progress_translate)

        # --- Bouton génération MKV ---
        self.btn_generate_mkv = QPushButton("🎬 Générer MKV avec sous-titres")
        self.btn_generate_mkv.clicked.connect(self.generate_mkv)
        layout.addWidget(self.btn_generate_mkv)

        self.progress_mkv = QProgressBar()
        self.progress_mkv.setMaximum(0)
        layout.addWidget(self.progress_mkv)

        # --- Zone de texte pour affichage progression ---
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        layout.addWidget(self.progress_text)

        self.setLayout(layout)

        # Stockage des fichiers
        self.audio_path = ""
        self.srt_en = ""
        self.srt_translated = []
        self.mkv_output = ""

    # --- Fonctions boutons ---
    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner vidéo", "", "Videos (*.mp4 *.mkv)"
        )
        if file_path:
            self.video_path = file_path
            base_name = Path(file_path).stem
            self.output_dir = os.path.join(Path(file_path).parent, f"{base_name}_output")
            os.makedirs(self.output_dir, exist_ok=True)
            self.label_video.setText(f"Vidéo sélectionnée : {Path(file_path).name}")

    def extract_audio(self):
        if not self.video_path:
            self.progress_text.append("❌ Sélectionnez d'abord une vidéo")
            return
        self.audio_path = os.path.join(self.output_dir, "audio.wav")
        self.run_in_thread(extraire_audio_ffmpeg, self.video_path, self.audio_path, self.progress_audio)

    def transcribe_audio(self):
        if not self.audio_path or not os.path.exists(self.audio_path):
            self.progress_text.append("❌ Extraire l'audio avant la transcription")
            return
        self.srt_en = os.path.join(self.output_dir, Path(self.video_path).stem + "_en.srt")
        self.run_in_thread(self._transcribe_wrapper, self.progress_transcribe)

    def _transcribe_wrapper(self, progress_bar):
        transcription = transcrire_audio_fast(self.audio_path, model_size="small")
        convertir_en_srt(transcription, self.srt_en)

    def translate_srt(self):
        if not self.srt_en or not os.path.exists(self.srt_en):
            self.progress_text.append("❌ Transcrire en anglais avant de traduire")
            return
        langs = [self.lang_list.item(i).text() for i in range(self.lang_list.count())
                 if self.lang_list.item(i).checkState() == Qt.Checked]
        if not langs:
            self.progress_text.append("❌ Sélectionnez au moins une langue")
            return
        self.srt_translated = [os.path.join(self.output_dir,
                                            f"{Path(self.srt_en).stem}_{lang}.srt") for lang in langs]
        for lang, output in zip(langs, self.srt_translated):
            self.run_in_thread(traduire_srt, self.srt_en, output, lang, self.progress_translate)

    def generate_mkv(self):
        if not self.video_path or not self.srt_en or not self.srt_translated:
            self.progress_text.append("❌ Assurez-vous que vidéo et sous-titres existent")
            return
        self.mkv_output = os.path.join(self.output_dir, Path(self.video_path).stem + "_subtitled.mkv")
        self.run_in_thread(create_mkv_with_multiple_subs, self.video_path,
                           [self.srt_en] + self.srt_translated, self.mkv_output, self.progress_mkv)

    # --- Lancer fonction dans thread ---
    def run_in_thread(self, func, *args):
        worker = Worker(func, *args)
        worker.progress_signal.connect(self.update_progress)
        worker.finished_signal.connect(self.update_progress)
        worker.start()

    def update_progress(self, text):
        self.progress_text.append(text)
        self.progress_text.verticalScrollBar().setValue(
            self.progress_text.verticalScrollBar().maximum()
        )

# --- Main ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SubtitleGUI()
    window.show()
    sys.exit(app.exec())
