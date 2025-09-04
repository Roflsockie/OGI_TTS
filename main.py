import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
import edge_tts
import asyncio
import requests
from langdetect import detect

# Disable Qt warnings
os.environ['QT_LOGGING_RULES'] = '*.warning=false'

# Global exception handler to keep terminal open
def exception_hook(exctype, value, traceback):
    print(f"Uncaught exception: {exctype} {value}")
    print("Traceback:")
    import traceback as tb
    tb.print_tb(traceback)
    input("Press Enter to exit...")

sys.excepthook = exception_hook

# Add ffmpeg directory to PATH
ffmpeg_dir = r'M:\AI\HGF TTS\ffmpeg\bin'
if os.path.exists(ffmpeg_dir):
    os.environ['PATH'] += os.pathsep + ffmpeg_dir
    print(f"Added FFMPEG path: {ffmpeg_dir}")
else:
    print("FFMPEG directory not found, using system FFMPEG if available")

class LanguageWindow(QMainWindow):
    def __init__(self, supported_languages, callback):
        super().__init__()
        uic.loadUi(r'M:\AI\HGF TTS\language_windos.ui', self)
        self.callback = callback
        self.supported_languages = supported_languages
        # Assuming buttons are pushButton, pushButton_2, etc.
        buttons = [self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_4]
        for i, lang in enumerate(supported_languages):
            if i < len(buttons):
                buttons[i].setText(lang)
                buttons[i].clicked.connect(lambda checked, l=lang: self.select_language(l))
        for i in range(len(supported_languages), len(buttons)):
            buttons[i].hide()

    def select_language(self, lang):
        self.callback(lang)
        self.close()

class TTSWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self, text, voice, output_file):
        super().__init__()
        self.text = text
        self.voice = voice
        self.output_file = output_file

    def run(self):
        print("Starting TTS...")
        self.progress.emit(10)
        self.log_signal.emit("Starting TTS... 10%")
        try:
            print("Using Edge TTS")
            self.progress.emit(20)
            self.log_signal.emit("Initializing Edge TTS... 20%")
            async def generate_tts():
                self.progress.emit(30)
                self.log_signal.emit("Preparing voice... 30%")
                communicate = edge_tts.Communicate(self.text, self.voice)
                self.progress.emit(50)
                self.log_signal.emit("Generating speech... 50%")
                await communicate.save(self.output_file)
                self.progress.emit(90)
                self.log_signal.emit("Saving audio... 90%")
            asyncio.run(generate_tts())
            self.progress.emit(100)
            self.log_signal.emit("TTS completed 100%")
            self.finished.emit("TTS completed")
            print("TTS finished successfully")
        except Exception as e:
            print(f"TTS Error: {e}")
            self.finished.emit(f"Error: {e}")

class VoiceWindow(QMainWindow):
    def __init__(self, voices, callback):
        super().__init__()
        uic.loadUi(r'M:\AI\HGF TTS\voice_window.ui', self)
        self.callback = callback
        self.voices = voices
        buttons = [self.pushButton, self.pushButton_2]
        for i, voice in enumerate(voices):
            if i < len(buttons):
                buttons[i].setText(voice)
                buttons[i].clicked.connect(lambda checked, v=voice: self.select_voice(v))
        for i in range(len(voices), len(buttons)):
            buttons[i].hide()

    def select_voice(self, voice):
        self.callback(voice)
        self.close()

class ModelWindow(QMainWindow):
    def __init__(self, available_models, callback):
        super().__init__()
        uic.loadUi(r'M:\AI\HGF TTS\model_window.ui', self)
        self.callback = callback
        self.available_models = available_models
        buttons = [self.pushButton, self.pushButton_2, self.pushButton_3]
        for i, model in enumerate(available_models):
            if i < len(buttons):
                buttons[i].setText(model)
                buttons[i].clicked.connect(lambda checked, m=model: self.select_model(m))
        for i in range(len(available_models), len(buttons)):
            buttons[i].hide()

    def select_model(self, model):
        self.callback(model)
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'M:\AI\HGF TTS\main_window.ui', self)
        self.setWindowTitle("OGI TTS")

        # Add log to scrollArea
        self.log = QTextEdit()
        layout = QVBoxLayout(self.scrollAreaWidgetContents)
        layout.addWidget(self.log)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        # Variables
        self.selected_file = None
        self.selected_model = None
        self.selected_language = None
        self.selected_text_language = None
        self.selected_voice = None
        self.text_content = ""
        self.available_models = ["Edge TTS"]

        # Connect buttons
        self.pushButton.clicked.connect(self.import_text)  # Import Text
        self.pushButton_2.clicked.connect(self.chose_model)  # Chose Model
        self.pushButton_3.clicked.connect(self.chose_voice)  # Chose Voice
        self.pushButton_4.clicked.connect(self.play_example)  # Play example
        self.pushButton_5.clicked.connect(self.text_to_speech)  # Text to Speech
        self.pushButton_6.clicked.connect(self.copy_log)  # Copy LOG
        self.pushButton_7.clicked.connect(self.clear_log)  # Clear LOG

        self.pushButton_8.clicked.connect(self.open_result_folder)  # Open Result Folder

        self.progressBar.setVisible(False)
        self.progressBar.setFormat("%p%")

        # Supported languages mapping
        self.language_map = {
            "English": "en-US",
            "Russian": "ru-RU",
            "Ukrainian": "uk-UA",
            "Japanese": "ja-JP"
        }
        self.voice_map = {
            "en-US": {"Male": "en-US-ZiraNeural", "Female": "en-US-AriaNeural"},
            "ru-RU": {"Male": "ru-RU-DmitryNeural", "Female": "ru-RU-SvetlanaNeural"},
            "uk-UA": {"Male": "uk-UA-OstapNeural", "Female": "uk-UA-PolinaNeural"},
            "ja-JP": {"Male": "ja-JP-KeitaNeural", "Female": "ja-JP-NanamiNeural"}
        }
        self.voice_short = {
            "en-US-ZiraNeural": "zira",
            "en-US-AriaNeural": "aria",
            "ru-RU-DmitryNeural": "dmitry",
            "ru-RU-SvetlanaNeural": "svetlana",
            "uk-UA-OstapNeural": "ostap",
            "uk-UA-PolinaNeural": "polina",
            "ja-JP-KeitaNeural": "keita",
            "ja-JP-NanamiNeural": "nanami"
        }
        self.supported_languages = list(self.language_map.keys())
        self.test_mode = False  # Set to False for normal use
        if self.test_mode:
            self.run_test()

    def log_message(self, message, color="black"):
        self.log.append(f'<span style="color:{color};">{message}</span>')

    def import_text(self):
        program_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Text File", program_dir, "Text Files (*.txt *.docx)")
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            try:
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.text_content = f.read()
                elif file_path.endswith('.docx'):
                    # For docx, need python-docx
                    from docx import Document
                    doc = Document(file_path)
                    self.text_content = '\n'.join([para.text for para in doc.paragraphs])
                char_count = len(self.text_content)
                # Detect language
                try:
                    detected_lang = detect(self.text_content)
                    if detected_lang == 'ru':
                        self.selected_text_language = "Russian"
                    elif detected_lang == 'en':
                        self.selected_text_language = "English"
                    elif detected_lang == 'uk':
                        self.selected_text_language = "Ukrainian"
                    elif detected_lang == 'ja':
                        self.selected_text_language = "Japanese"
                    else:
                        self.selected_text_language = "English"  # default
                    self.log_message(f"Detected language: {self.selected_text_language}", "green")
                    self.selected_language = self.language_map[self.selected_text_language]
                    # Automatically proceed to choose model
                    self.chose_model()
                except:
                    self.selected_text_language = "English"  # default if detection fails
                    self.selected_language = self.language_map[self.selected_text_language]
                    self.log_message("Language detection failed, defaulting to English", "yellow")
                    self.chose_model()
                self.log_message(f"File: <span style='color:yellow;'>{filename}</span>", "green")
                self.log_message(f"Characters: <span style='color:cyan;'>{char_count}</span>", "green")
            except Exception as e:
                self.log_message(f"Error importing file: {e}", "red")

    def chose_model(self):
        if not self.selected_text_language:
            self.log_message("Import text first", "red")
            return
        self.model_window = ModelWindow(self.available_models, self.on_model_chosen)
        self.model_window.show()

    def on_model_chosen(self, model):
        self.selected_model = model
        self.log_message(f"Model selected: {model}", "green")
        # Now suggest voices
        self.chose_voice()

    def chose_voice(self):
        if not self.selected_language:
            self.log_message("Select language first", "red")
            return
        voices = ["Male", "Female"]
        self.voice_window = VoiceWindow(voices, self.on_voice_chosen)
        self.voice_window.show()

    def on_voice_chosen(self, voice):
        self.selected_voice = voice
        self.log_message(f"Voice selected: {voice}", "green")

    def generate_filename(self, is_example=False):
        if not self.selected_text_language or not self.selected_language or not self.selected_voice:
            return "output.wav"  # fallback
        
        lang_code = {
            "Russian": "ru",
            "English": "eng",
            "Ukrainian": "ua",
            "Japanese": "jp"
        }.get(self.selected_text_language, "unk")
        
        voice_full = self.voice_map[self.selected_language][self.selected_voice]
        voice_tag = self.voice_short.get(voice_full, self.selected_voice.lower()[:3])
        
        if is_example:
            return f"example_edge{voice_tag}_{lang_code}.wav"
        else:
            return f"{lang_code}_output_edge{voice_tag}.wav"

    def play_example(self):
        example_text = self.lineEdit.text()
        if not example_text:
            self.log_message("Enter text for example", "red")
            return
        if not self.selected_language or not self.selected_voice:
            self.log_message("Select language and voice first", "red")
            return
        voice = self.voice_map[self.selected_language][self.selected_voice]
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, 'tts_audio')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.log_message(f"Created folder: <b>{output_dir}</b>", "white")
        output_file = os.path.join(output_dir, self.generate_filename(is_example=True))
        self.progressBar.setVisible(True)
        self.progressBar.setValue(5)
        self.worker = TTSWorker(example_text, voice, output_file)
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.log_signal.connect(lambda msg: self.log_message(msg, "blue"))
        self.worker.finished.connect(self.on_tts_finished)
        self.worker.start()

    def text_to_speech(self):
        if not self.text_content:
            self.log_message("Import text first", "red")
            return
        if not self.selected_language or not self.selected_voice:
            self.log_message("Select language and voice first", "red")
            return
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, 'tts_audio')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.log_message(f"Created folder: <b>{output_dir}</b>", "white")
        output_file = os.path.join(output_dir, self.generate_filename(is_example=False))
        voice = self.voice_map[self.selected_language][self.selected_voice]
        self.progressBar.setVisible(True)
        self.progressBar.setValue(5)
        self.worker = TTSWorker(self.text_content, voice, output_file)
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.log_signal.connect(lambda msg: self.log_message(msg, "blue"))
        self.worker.finished.connect(self.on_tts_finished)
        self.worker.start()

    def copy_log(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.log.toPlainText())
            self.log_message("Log copied to clipboard", "green")
        else:
            self.log_message("Clipboard not available", "red")

    def clear_log(self):
        self.log.clear()

    def open_result_folder(self):
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, 'tts_audio')
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            self.log_message("tts_audio folder does not exist yet", "red")

    def on_tts_finished(self, msg):
        self.log_message(msg, "green")
        self.progressBar.setValue(100)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.progressBar.setVisible(False))  # Задержка 1 секунда

    def run_test(self):
        # Auto test all languages
        self.test_languages = ["English", "Ukrainian", "Russian", "Japanese"]
        self.test_files = ["eng_story.txt", "ua_story.txt", "ru_story.txt", "jp_story.txt"]
        self.test_outputs = ["eng_test.wav", "ua_test.wav", "ru_test.wav", "jp_test.wav"]
        self.test_index = 0
        self.run_next_test()

    def run_next_test(self):
        if self.test_index >= len(self.test_languages):
            print("All tests completed")
            return
        
        lang = self.test_languages[self.test_index]
        file = self.test_files[self.test_index]
        output = self.test_outputs[self.test_index]
        
        print(f"Testing {lang} with {file}")
        # Import file
        test_file = os.path.join(r'M:\AI\HGF TTS', file)
        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                self.text_content = f.read()
            self.log_message(f"Test file {file} imported", "green")
        else:
            print(f"File {file} not found")
            self.test_index += 1
            self.run_next_test()
            return
        
        # Select model
        self.selected_model = "Edge TTS"
        # Select language
        self.selected_language = self.language_map[lang]
        self.log_message(f"Language selected: {lang}", "green")
        # Run TTS
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, 'tts_audio')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created folder: {output_dir}")
        output_file = os.path.join(output_dir, output)
        voice = self.voice_map[self.selected_language]
        self.progressBar.setVisible(True)
        self.progressBar.setValue(5)
        self.worker = TTSWorker(self.text_content, voice, output_file)
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.log_signal.connect(lambda msg: self.log_message(msg, "blue"))
        self.worker.finished.connect(self.on_test_finished)
        self.worker.start()

    def on_test_finished(self, msg):
        print(f"Test {self.test_index + 1} finished: {msg}")
        self.test_index += 1
        self.run_next_test()

if __name__ == "__main__":
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        if app.instance() is not None:
            sys.exit(app.exec_())
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
