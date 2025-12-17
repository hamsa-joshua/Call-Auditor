import whisper
import json
import os
import senko 
class AudioProcessor:
    def __init__(self, model_size="base", device="auto"):
        """
        Initialize Whisper and Senko models.
        """
        self.device = device
        
        # Initialize Whisper
        print(f"Loading Whisper model: {model_size}...")
        self.model = whisper.load_model(model_size, device=device)
        print("Whisper model loaded.")
        
        # Initialize Senko
        print("Loading Senko model...")
        self.diarizer = senko.Diarizer(device=device, warmup=True, quiet=False)
        print("Senko model loaded.")
    def process_audio(self, file_path):
        """
        Process audio file: Transcribe & Diarize using user's specific logic.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        # 1. Diarization (Senko)
        print(f"Diarizing {file_path}...")
        dia_result = self.diarizer.diarize(file_path, generate_colors=False)
        senko_segments = dia_result["merged_segments"] # User's code key
        # 2. Transcription (Whisper)
        print(f"Transcribing {file_path}...")
        whisper_result = self.model.transcribe(file_path)
        # 3. Merge (User's Midpoint Logic)
        diarized_transcript = []
        for seg in whisper_result["segments"]:
            mid_time = (seg["start"] + seg["end"]) / 2
            # Find speaker
            speaker_label = "Unknown"
            for s in senko_segments:
                # User logic: check if midpoint is within senko segment
                if s["start"] <= mid_time <= s["end"]:
                    speaker_label = s["speaker"]
                    break 
            diarized_transcript.append({
                "start": seg["start"],
                "end": seg["end"],
                "speaker": speaker_label,
                "text": seg["text"].strip()
            })
        return diarized_transcript
    def export_to_json(self, transcript_data, output_path):
        with open(output_path, 'w') as f:
            json.dump(transcript_data, f, indent=4)
        return output_path