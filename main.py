import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import speech_recognition as sr
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading
import queue
import time
from customtkinter import *

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("Google API key not set in the environment variable 'GOOGLE_API_KEY' or .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
MODEL = genai.GenerativeModel('gemini-pro')

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

DEFAULT_PROMPT = "Correct the following text for grammar and spelling errors in {language}. Provide detailed feedback. If there are no errors return text as is: {text}"

class GrammarCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Grammar Checker with Gemini")

        # UI Elements
        self.language_frame = self.create_language_section()
        self.text_input_frame = self.create_text_input_section()
        self.audio_frame = self.create_audio_section()
        self.display_frame = self.create_display_section()

        self.recognizer = sr.Recognizer()
        self.is_recording = False
        self.audio_settings = {}
        self.custom_prompt = DEFAULT_PROMPT
        self.audio_source_list = self.get_microphone_names()
        self.recording_queue = queue.Queue()  # Queue to hold recording segments
        self.gemini_queue = queue.Queue() # Queue to hold requests for gemini

    def create_language_section(self):
        language_frame = CTkFrame(self.root)
        language_frame.pack(pady=5)

        language_label = CTkLabel(language_frame, text="Select Language:")
        language_label.pack(side="left", padx=5)

        self.language_var = tk.StringVar(value='en-US')
        # Use variable= instead of textvariable=
        self.language_dropdown = CTkComboBox(language_frame, variable=self.language_var, values=list(LANGUAGES.keys()))
        self.language_dropdown.pack(side="left", padx=5)
        # Use configure instead of config
        self.language_dropdown.configure(width=20)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.update_language_description)
        
        self.language_description = CTkLabel(language_frame, text=LANGUAGES['en-US'])
        self.language_description.pack(side="left", padx=5)
        return language_frame
    
    def create_text_input_section(self):
        text_input_frame = CTkFrame(self.root)
        text_input_frame.pack(pady=5)

        self.text_input_button = CTkButton(text_input_frame, text="Enter Text", command=self.enter_text)
        self.text_input_button.pack(side="left", padx=5)
        return text_input_frame

    def create_audio_section(self):
        audio_frame = CTkFrame(self.root)
        audio_frame.pack(pady=5)

        self.audio_settings_button = CTkButton(audio_frame, text="Audio Settings", command=self.open_audio_settings)
        self.audio_settings_button.pack(side="left", padx=5)

        self.record_button = CTkButton(audio_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(side="left", padx=5)
        return audio_frame
    
    def create_display_section(self):
        display_frame = CTkFrame(self.root)
        display_frame.pack(pady=5)

        # Transcription Display
        transcript_label = CTkLabel(display_frame, text="Transcribed Text:")
        transcript_label.pack(pady=5)

        self.transcript_display = scrolledtext.ScrolledText(display_frame, height=5, width=60, wrap="word",fg = "white",  bg = "#353535")
        self.transcript_display.pack(pady=5)
        self.transcript_display.configure(state='disabled')

        # Correction & Feedback Display
        correction_label = CTkLabel(display_frame, text="Corrected Text & Feedback:")
        correction_label.pack(pady=5)

        self.corrected_text_display = scrolledtext.ScrolledText(display_frame, height=10, width=60, wrap="word", fg = "white",  bg = "#353535")
        self.corrected_text_display.pack(pady=5)
        self.corrected_text_display.configure(state='disabled')
        
        # Gemini Prompt Customization
        prompt_button = CTkButton(display_frame, text="Customize Prompt", command=self.customize_prompt)
        prompt_button.pack(pady=5)

        # Status Label
        self.status_label = CTkLabel(display_frame, text="")
        self.status_label.pack(pady=5)

        self.loading_label = CTkLabel(display_frame, text="", image=None)  # Loading indicator
        self.loading_label.pack(pady=5)
        
        return display_frame
    
    def update_language_description(self, event):
            selected_code = self.language_var.get()
            self.language_description.configure(text=LANGUAGES.get(selected_code, "Language not found"))

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
        audio_source_dropdown = ttk.Combobox(settings_window, textvariable=audio_source_var, values=self.audio_source_list)
        audio_source_dropdown.grid(row=1, column=1, padx=5, pady=5)
        
        def save_audio_settings():
            self.audio_settings = {"duration": duration_scale.get(), "audio_source":audio_source_var.get()}
            settings_window.destroy()

        save_button = ttk.Button(settings_window, text="Save", command=save_audio_settings)
        save_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    
    def get_microphone_names(self):
        try:
             return sr.Microphone.list_microphone_names()
        except Exception as e:
            messagebox.showerror("Microphone Error", f"Could not list microphones: {e}")
            return ["default"] #return default if there is no available microphone
    
    def enter_text(self):
        text = simpledialog.askstring("Input Text", "Enter text to check:")
        if text:
            self.transcript_display.configure(state='normal')
            self.transcript_display.delete(1.0, tk.END)
            self.transcript_display.insert(tk.END, text)
            self.transcript_display.configure(state='disabled')
            self.status_label.configure(text="Processing...")
            self.process_text_for_correction(text, self.language_var.get())
    
    def toggle_recording(self):
        if not self.is_recording:
            self.start_realtime_recording()
        else:
             self.stop_recording()

    def start_realtime_recording(self):
        self.is_recording = True
        # Use configure instead of config
        self.record_button.configure(text="Stop Recording")
        self.status_label.configure(text="Recording...")
        self.transcript_display.configure(state='normal')
        self.transcript_display.delete(1.0, tk.END)
        self.transcript_display.configure(state='disabled')
        self.corrected_text_display.configure(state='normal')
        self.corrected_text_display.delete(1.0, tk.END)
        self.corrected_text_display.configure(state='disabled')

        language = self.language_var.get()
        
        # Start two threads, one for recording and one for processing
        self.recording_thread = threading.Thread(target=self.record_audio_stream, args=(language,), daemon=True)
        self.processing_thread = threading.Thread(target=self.process_audio_queue, daemon=True)
        self.gemini_thread = threading.Thread(target=self.process_gemini_queue, daemon=True)

        self.recording_thread.start()
        self.processing_thread.start()
        self.gemini_thread.start()


    def record_audio_stream(self, language):
        try:
            microphone_name = self.audio_settings.get("audio_source", "default")
            microphone_index = None
            if microphone_name != "default":
                try:
                    microphone_index = self.audio_source_list.index(microphone_name)
                except ValueError:
                    microphone_index = None
                    self.root.after(0, self.status_label.configure, {"text": "Selected Microphone Not Available, Using Default"})
            
            with sr.Microphone(device_index=microphone_index) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                
                while self.is_recording:
                    try:
                        audio = self.recognizer.listen(source, phrase_time_limit=3) # Limit phrases to 3 seconds
                        self.recording_queue.put((audio, language)) # Pass the audio to the queue
                    except sr.WaitTimeoutError:
                        pass
        except Exception as e:
            self.root.after(0, self.status_label.configure, {"text": f"Recording error: {e}"})
        finally:
           self.recording_queue.put(None) #signal the processign queue that recording is done
    
    def process_audio_queue(self):
        while True:
           item = self.recording_queue.get()
           if item is None:
              self.recording_queue.task_done()
              break
           audio, language = item
           self.process_audio(audio, language)
           self.recording_queue.task_done()

    def process_audio(self, audio, language):
        try:
                text = self.recognizer.recognize_google(audio, language=language)
                self.root.after(0, self.update_transcript, text)
                self.gemini_queue.put((text, language)) # Add request to Gemini queue
        except sr.UnknownValueError:
             self.root.after(0, self.status_label.configure, {"text": "Could not understand audio"})
        except sr.RequestError as e:
            self.root.after(0, self.status_label.configure, {"text": f"Could not request results from Google Speech Recognition service; {e}"})
        except Exception as e:
            self.root.after(0, self.status_label.configure, {"text": f"An unexpected error occured: {e}"})
    
    def process_gemini_queue(self):
        while True:
           item = self.gemini_queue.get()
           if item is None:
                self.gemini_queue.task_done()
                break
           text, language = item
           self.process_text_for_correction(text, language, append=True)
           self.gemini_queue.task_done()

    def update_transcript(self, text):
            self.transcript_display.configure(state='normal')
            self.transcript_display.insert(tk.END, " "+text)
            self.transcript_display.configure(state='disabled')
    
    def stop_recording(self):
        self.is_recording = False # Immediately set is_recording to false to stop recording from continuing
        self.record_button.configure(text="Start Recording") #change button text
        self.status_label.configure(text="Processing...") # Notify the user that the last segment is being processed
        
        # Make sure all queues are empty and threads have done their work
        # check that the recording thread actually exist and is running
        if hasattr(self, "recording_thread") and self.recording_thread.is_alive():
             self.recording_thread.join(timeout=5)  # Wait for the recording thread to finish
             if self.recording_thread.is_alive():
                 self.root.after(0, self.status_label.configure, {"text": "Recording thread did not finish in time"}) # If it does not finish within the timeout, let the user know
        
        self.gemini_queue.put(None)  # Signal the gemini processing thread to stop.
        self.recording_queue.put(None) # signal the processing queue to stop
        self.processing_thread.join(timeout=5) # wait for the processing thread to finish
        if self.processing_thread.is_alive():
            self.root.after(0, self.status_label.configure, {"text": "Processing thread did not finish in time"})# If it does not finish within the timeout, let the user know
        self.gemini_thread.join(timeout=5)# wait for the gemini thread to finish
        if self.gemini_thread.is_alive():
            self.root.after(0, self.status_label.configure, {"text": "Gemini thread did not finish in time"})# If it does not finish within the timeout, let the user know
        
        self.status_label.configure(text="Done") # show user it is finished.
        self.root.after(0, self.loading_label.configure, {"image": None}) #remove loading image


    def process_text_for_correction(self, text, language, append=False):
            prompt = self.custom_prompt.format(language=language, text=text)
            self._run_gemini_request(prompt, append)
    
    def _run_gemini_request(self, prompt, append):
        try:
            self.root.after(0, self.show_loading_indicator) # show the loading message
            response = MODEL.generate_content(prompt)
            corrected_text = response.text
            self.root.after(0, self.update_correction_text, corrected_text, append)  # Update UI on main thread
            self.root.after(0, self.hide_loading_indicator) # hide the loading message

        except Exception as e:
            error_message = f"Error checking grammar: {e}"
            self.root.after(0, self.status_label.config, {"text": error_message})
            self.root.after(0, self.update_correction_text, "Could not process with Gemini. See the error message above.", append)
            self.root.after(0, self.hide_loading_indicator)
    
    def show_loading_indicator(self):
        self.loading_label.configure(text="Loading...")
        # Add an animated loading gif to make it look nicer.
        # Use something like: self.loading_gif = tk.PhotoImage(file="loading.gif") 
        #                        self.loading_label.config(image=self.loading_gif)


    def hide_loading_indicator(self):
        self.loading_label.configure(text="", image=None)

    def update_correction_text(self, corrected_text, append=False):
        self.corrected_text_display.configure(state='normal')
        if append:
            self.corrected_text_display.insert(tk.END, " "+corrected_text)
        else:
           self.corrected_text_display.delete(1.0, tk.END)
           self.corrected_text_display.insert(tk.END, corrected_text)
        self.corrected_text_display.configure(state='disabled')
    
    def customize_prompt(self):
        prompt = simpledialog.askstring("Customize Prompt", "Enter your custom prompt:", initialvalue=self.custom_prompt)
        if prompt:
           self.custom_prompt = prompt
        
        # Add reset option if wanted
        reset = messagebox.askyesno("Reset Prompt","Do you want to reset the prompt to the default?")
        if reset:
            self.custom_prompt = DEFAULT_PROMPT

if __name__ == "__main__":
    root = CTk()
    set_default_color_theme("green")
    app = GrammarCheckerApp(root)
    root.mainloop()