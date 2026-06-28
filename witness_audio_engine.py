import os
from elevenlabs.client import ElevenLabs

class WitnessAudioEngine:
    def __init__(self, api_key="b98e1d9774126e36f3d1f515bde9625019ebd997b2558bf61752623d6d278c69"):
        print("Initializing Witness Audio Intelligence Engine (ElevenLabs Scribe)...")
        self.api_key = api_key
        # Ensure we have the client initialized
        self.client = ElevenLabs(api_key=self.api_key)

    def analyze_audio(self, audio_path, target_language="English"):
        """
        Transcribes witness audio to text using ElevenLabs Speech-to-Text.
        """
        print(f"Transcribing audio from: {audio_path} into {target_language}")
        
        # Map selected language to ISO 639-3 code supported by ElevenLabs
        lang_map = {
            "English": "eng",
            "Spanish": "spa",
            "French": "fra",
            "Hindi": "hin",
            "German": "deu",
            "Mandarin": "cmn",
            "Tamil": "tam"
        }
        lang_code = lang_map.get(target_language, "eng")
        
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v1",
                language_code=lang_code
            )
            
        # The API returns a Transcription object which contains the text.
        text = transcript.text if hasattr(transcript, 'text') else str(transcript)
        
        # We can extract entities later using NLP, for now just mock empty entities
        return {
            "transcript": text,
            "entities": []
        }

if __name__ == "__main__":
    import sys
    engine = WitnessAudioEngine()
    print(engine.process_audio("sample_witness.wav"))
