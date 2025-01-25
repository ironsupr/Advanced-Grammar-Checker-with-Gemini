import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog
import speech_recognition as sr
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading
import queue

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("Google API key not set in the environment variable 'GOOGLE_API_KEY' or .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')

# Language Codes Mapping
LANGUAGES = {
    'en-US': 'English (US)',
    'es-ES': 'Spanish (Spain)',
    'fr-FR': 'French (France)',
    'de-DE': 'German (Germany)',
    'it-IT': 'Italian (Italy)',
    'ja-JP': 'Japanese (Japan)',
    'ko-KR': 'Korean (South Korea)',
    'zh-CN': 'Chinese (China)',
    'pt-BR': 'Portuguese (Brazil)',
    'ru-RU': 'Russian (Russia)',
    'ar-SA': 'Arabic (Saudi Arabia)',
    'hi-IN': 'Hindi (India)',
    'nl-NL': 'Dutch (Netherlands)',
    'sv-SE': 'Swedish (Sweden)',
    'pl-PL': 'Polish (Poland)',
    'tr-TR': 'Turkish (Turkey)',
    'vi-VN': 'Vietnamese (Vietnam)'
}

class GrammarCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Grammar Checker with Gemini")

        # UI Elements
        self.create_ui()

        self.recognizer = sr.Recognizer()
        self.is_recording = False
        self.audio_queue = queue.Queue()


    def create_ui(self):
        # Language Selection
        self.language_label = ttk.Label(self.root, text="Select Language:")
        self.language_label.pack(pady=5)

        self.language_var = tk.StringVar(value='en-US')
        self.language_dropdown = ttk.Combobox(self.root, textvariable=self.language_var, values=list(LANGUAGES.keys()))
        self.language_dropdown.pack(pady=5)
        self.language_dropdown.config(width=20)

        self.language_dropdown.bind("<<ComboboxSelected>>", self.update_language_description)
        self.language_description = ttk.Label(self.root, text=LANGUAGES['en-US'])
        self.language_description.pack(pady=5)
        
        # Audio Settings Button
        self.audio_settings_button = ttk.Button(self.root, text="Audio Settings", command=self.open_audio_settings)
        self.audio_settings_button.pack(pady=5)


        # Text Input Option
        self.text_input_button = ttk.Button(self.root, text="Enter Text", command=self.enter_text)
        self.text_input_button.pack(pady=5)

        # Recording Button
        self.record_button = ttk.Button(self.root, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=10)
        
        # Transcription Display
        self.transcript_label = ttk.Label(self.root, text="Transcribed Text:")
        self.transcript_label.pack(pady=5)

        self.transcript_text = scrolledtext.ScrolledText(self.root, height=5, width=60, wrap="word")
        self.transcript_text.pack(pady=5)
        self.transcript_text.config(state='disabled')

        # Correction & Feedback Display
        self.correction_label = ttk.Label(self.root, text="Corrected Text & Feedback:")
        self.correction_label.pack(pady=5)

        self.correction_text = scrolledtext.ScrolledText(self.root, height=10, width=60, wrap="word")
        self.correction_text.pack(pady=5)
        self.correction_text.config(state='disabled')
        
         # Gemini Prompt Customization
        self.prompt_button = ttk.Button(self.root, text="Customize Prompt", command=self.customize_prompt)
        self.prompt_button.pack(pady=5)
        self.custom_prompt = "Correct the following text for grammar and spelling errors in {language}. Provide detailed feedback. If there are no errors return text as is: {text}"

        # Status Label
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack(pady=5)
        
    
    def update_language_description(self, event):
            selected_code = self.language_var.get()
            self.language_description.config(text=LANGUAGES.get(selected_code, "Language not found"))

    def open_audio_settings(self):
        # Placeholder for future audio parameter adjustment dialog
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Audio Settings")

        # Sample slider to select the recording duration
        duration_label = ttk.Label(settings_window, text="Recording Duration:")
        duration_label.grid(row=0, column=0, padx=5, pady=5)
        
        duration_scale = tk.Scale(settings_window, from_=1, to=10, orient="horizontal")
        duration_scale.grid(row=0, column=1, padx=5, pady=5)
        
        #  Sample options for audio source
        audio_source_label = ttk.Label(settings_window, text="Audio Source:")
        audio_source_label.grid(row=1, column=0, padx=5, pady=5)

        audio_source_var = tk.StringVar(value="default")
        audio_source_dropdown = ttk.Combobox(settings_window, textvariable=audio_source_var, values=["default"])
        audio_source_dropdown.grid(row=1, column=1, padx=5, pady=5)

        def save_audio_settings():
            self.audio_settings = {"duration": duration_scale.get(), "audio_source":audio_source_var.get()}
            settings_window.destroy()

        save_button = ttk.Button(settings_window, text="Save", command=save_audio_settings)
        save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
    def enter_text(self):
        text = simpledialog.askstring("Input Text", "Enter text to check:")
        if text:
            self.transcript_text.config(state='normal')
            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.insert(tk.END, text)
            self.transcript_text.config(state='disabled')
            self.status_label.config(text="Processing...")
            self.check_grammar(text, self.language_var.get())
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_realtime_recording()
        else:
             self.stop_recording()

    def start_realtime_recording(self):
            self.is_recording = True
            self.record_button.config(text="Stop Recording")
            self.status_label.config(text="Recording...")
            self.transcript_text.config(state='normal')
            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.config(state='disabled')
            self.correction_text.config(state='normal')
            self.correction_text.delete(1.0, tk.END)
            self.correction_text.config(state='disabled')

            language = self.language_var.get()
            self.audio_queue.queue.clear() # clear previous audio segments
            self.recording_thread = threading.Thread(target=self.record_audio_stream, args=(language,))
            self.recording_thread.start()


    def record_audio_stream(self, language):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                
                while self.is_recording:
                    try:
                         audio = self.recognizer.listen(source, phrase_time_limit=3) #Limit phrases to 3 seconds
                         self.audio_queue.put((audio, language))
                         threading.Thread(target=self.process_audio, args=(audio, language), daemon=True).start()
                    except sr.WaitTimeoutError:
                        pass
        except Exception as e:
            self.status_label.config(text=f"Recording error: {e}")
    
    def process_audio(self, audio, language):
        try:
                text = self.recognizer.recognize_google(audio, language=language)
                self.update_transcript(text)
        except sr.UnknownValueError:
            self.status_label.config(text="Could not understand audio")
        except sr.RequestError as e:
           self.status_label.config(text=f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
             self.status_label.config(text=f"An unexpected error occured: {e}")

    def update_transcript(self, text):
            self.transcript_text.config(state='normal')
            self.transcript_text.insert(tk.END, " "+text)
            self.transcript_text.config(state='disabled')
            self.check_grammar(text, self.language_var.get(), append=True)


    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Start Recording")
        self.status_label.config(text="Processing last segment...")
        if hasattr(self, "recording_thread") and self.recording_thread.is_alive():
                self.recording_thread.join() # Join the thread so it can clean up the recording
        self.status_label.config(text="Done")


    def check_grammar(self, text, language, append=False):
        prompt = self.custom_prompt.format(language=language, text=text)
        try:
            response = model.generate_content(prompt)
            corrected_text = response.text
            self.update_correction_text(corrected_text, append)

        except Exception as e:
            self.status_label.config(text=f"Error checking grammar: {e}")
            self.update_correction_text("Could not process with Gemini. See the error message above.", append)


    def update_correction_text(self, corrected_text, append=False):
        self.correction_text.config(state='normal')
        if append:
            self.correction_text.insert(tk.END,  " "+corrected_text)
        else:
           self.correction_text.delete(1.0, tk.END)
           self.correction_text.insert(tk.END, corrected_text)
        self.correction_text.config(state='disabled')
    
    def customize_prompt(self):
        prompt = simpledialog.askstring("Customize Prompt", "Enter your custom prompt:", initialvalue=self.custom_prompt)
        if prompt:
           self.custom_prompt = prompt


if __name__ == "__main__":
    root = tk.Tk()
    app = GrammarCheckerApp(root)
    root.mainloop()