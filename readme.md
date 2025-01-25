# Advanced Grammar Checker with Gemini

This application is a desktop tool that leverages Google's Gemini Pro model for advanced grammar and spelling checks. It allows users to input text through direct typing or real-time speech recognition, offering corrections and detailed feedback.

## Features

-   **Multi-language Support:** Supports a wide range of languages for grammar checking, including English, Spanish, French, German, and many more.
-   **Text Input:** Allows users to directly input text for analysis.
-   **Real-time Speech Recognition:** Uses Google's Speech Recognition API for transcribing speech in real-time.
-   **Gemini Powered Correction:** Uses Google's Gemini Pro model for advanced grammar and spelling corrections, and provides detailed feedback.
-   **Customizable Prompt:** Allows users to customize the prompt sent to the Gemini model for fine-tuning the correction process.
-   **Audio Settings:** Allows for basic adjustments to recording duration and audio source.
-   **Responsive UI:** Employs threads for backend processes, ensuring the UI remains responsive.

## Getting Started

### Prerequisites

-   **Python 3.7 or higher**
-   **Google Cloud API Key** with access to the Gemini Pro model. You can create or find this in the [Google AI Studio](https://makersuite.google.com/app/apikey)
-   **Python Libraries:**
    -   `tkinter`
    -   `speechrecognition`
    -   `google-generativeai`
    -   `python-dotenv`

### Installation

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/ironsupr/Advanced-Grammar-Checker-with-Gemini.git
    cd Advanced-Grammar-Checker-with-Gemini
    ```

2.  **Install Required Libraries:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up the .env file**

  Create a `.env` file in the same directory as your python script. Add your Google AI API key to the `.env` file like so:

    ```
    GOOGLE_API_KEY="YOUR_API_KEY"
    ```

4.  **Run the Application:**

    ```bash
    python main.py
    ```
    

## Usage

1.  **Language Selection:** Choose your desired language from the dropdown menu.
2.  **Text Input:**
    -   Click "Enter Text" to type or paste text for checking.
3.  **Speech Recognition:**
    -   Click "Start Recording" to record your speech. The transcription and correction will be displayed in real-time. Click "Stop Recording" to stop and finish processing the last segment.
4.  **Audio Settings:**
    -   Click "Audio Settings" to adjust basic audio settings like recording duration and audio source.
5.  **Gemini Prompt:**
    -   Click "Customize Prompt" to modify the prompt for the Gemini model. You can customize how you want Gemini to correct the text. You can also revert to the default prompt by clicking the reset option when prompted.
6.  **View Output:**
    -   The transcribed text and the corrected version with feedback will be displayed in the corresponding text areas.
7.  **Status:** A status text is provided at the bottom of the application for updates.

## Development

### Code Structure

-   **`main.py`**: Contains the core application logic and UI setup.
-   **`.env`**: Stores the Google API key.
-   **`requirements.txt`**: Lists the project's dependencies.

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

### Planned Improvements

-   Progress bar during Gemini processing.
-   Improved error handling with user-friendly feedback.
-   Additional settings for Speech Recognition.
-   A "Clear" button to clear the text fields.
-   Partial transcription display
-   More robust configuration management for settings, language, and prompts.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Credits

-   [Google AI](https://ai.google/) for Gemini Pro and speech recognition APIs.
-   [Python](https://www.python.org/) for the language.
-   [Tkinter](https://docs.python.org/3/library/tkinter.html) for the UI library.
-   [python-dotenv](https://github.com/theskumar/python-dotenv) for environment variable management.
-   [speechrecognition](https://pypi.org/project/SpeechRecognition/) for speech recognition

## Contact

For questions, please reach out by creating an issue on the repository.