"""
"""

class Mic:
    def __init__(self):
        pass

    def listen(self):
        pass

    def transcription():
        """
        This function uses whisper to transcribe the audio files.
        """
        # Collecting .wav Files in Directory
        audioFiles = [file for file in os.listdir() if file.endswith(".wav")]

        model = whisper.load_model("medium")
        
        # Transcribing Each File
        for audio in audioFiles:
            print(f"Transcribing: {audio}")

            result = model.transcribe(
                audio,
                language = "en",
                task = "transcribe",
                condition_on_previous_text = False,
                hallucination_silence_threshold = 0.3
            )

            # Saving To .json File
            output = f"{os.path.splitext(audio)[0]}.json"
            with open(output, "w", encoding = "utf-8") as f:
                json.dump(result, f, ensure_ascii = False, indent = 2)

            print(f"Successfully Transcribed {audio}")
        
        return 0