import io
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from piper import PiperVoice, SynthesisConfig
import wave

from piper.phonemize_espeak import EspeakPhonemizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # up from main.py -> poc_tts -> src -> poc-tts
MODEL_PATH = PROJECT_ROOT / "static" / "pl_PL-darkman-medium.onnx"

PL_MODEL_PATH = PROJECT_ROOT / "static" / "pl_PL-darkman-medium.onnx"
EN_MODEL_PATH = PROJECT_ROOT / "static" / "en_US-lessac-medium.onnx"

pl_voice = PiperVoice.load(str(PL_MODEL_PATH))
en_voice = PiperVoice.load(str(EN_MODEL_PATH))

_espeak = EspeakPhonemizer(en_voice.espeak_data_dir)

def speak_pokemon_name(voice: PiperVoice, pronunciation: str) -> None:
    """Synthesize and play just the Pokémon name using English phonemes."""
    sentence_phonemes = _espeak.phonemize("en-us", pronunciation)
    phonemes = sentence_phonemes[0] if sentence_phonemes else []
    phoneme_block = "[[" + "".join(phonemes) + "]]"
    speak(voice, phoneme_block)

def speak_flavor_text(voice: PiperVoice, text: str) -> None:
    """Synthesize and play the flavor text normally in Polish."""
    speak(voice, text)

def announce_pokemon(pl_voice: PiperVoice, en_voice: PiperVoice, name: str, flavor_text: str) -> None:
    speak(en_voice, name, length_scale=1.2)          # e.g. "Charmander"
    speak(pl_voice, flavor_text, length_scale=1)   # Polish narration

def speak(voice: PiperVoice, text: str, length_scale: float = 1.0) -> None:
    syn_config = SynthesisConfig(length_scale=length_scale)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file, syn_config=syn_config)

    data, samplerate = sf.read(io.BytesIO(buffer.getvalue()))
    sd.play(data, samplerate)
    sd.wait()

if __name__ == "__main__":
    announce_pokemon(
        pl_voice,
        en_voice,
        name="Charmander",
        flavor_text="Pokemon typu ognistego. Zionie ogniem na tyle gorącym, że potrafi stopić głazy.",
    )