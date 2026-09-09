import io
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from piper import PiperVoice
import wave


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # up from main.py -> poc_tts -> src -> poc-tts
MODEL_PATH = PROJECT_ROOT / "static" / "pl_PL-darkman-medium.onnx"



def speak(voice: PiperVoice, text: str) -> None:
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    buffer.seek(0)  # rewind before reading back
    data, samplerate = sf.read(buffer)

    sd.play(data, samplerate)
    sd.wait()  # block until playback finishes

def main():
    voice = PiperVoice.load(str(MODEL_PATH))

    with wave.open("../../../static/audio/output_wav.wav", "wb") as wav_file:
        voice.synthesize_wav("Czarizard. Pokemon typu ognistego. Zionie ogniem na tyle gorącym, że potrafi stopić głazy. Znany z tego, że przypadkowo wywołuje pożary lasów.", wav_file)

if __name__ == "__main__":
    main()