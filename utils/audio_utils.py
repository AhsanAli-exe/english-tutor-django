import sounddevice as sd
import soundfile as sf
import tempfile
import os

def record_audio(seconds,sample_rate):
    print(f"\nRecording for {seconds} seconds... speak now.")
    recording = sd.rec(int(seconds * sample_rate),samplerate=sample_rate,channels=1,dtype="float32")
    sd.wait()
    
    # Create temporary WAV file (same as original working code)
    tmpf = tempfile.NamedTemporaryFile(delete=False,suffix=".wav")
    sf.write(tmpf.name, recording, sample_rate)
    print("Recording completed.")
    return tmpf.name

def transcribe_audio(audio_path, model, expected_sample_rate=16000):
    # Use the same approach as the original working code
    audio_array = None
    try:
        data, sr = sf.read(audio_path, dtype='float32')
        # ensure mono 1-D float32 array
        if hasattr(data, 'ndim') and data.ndim == 2:
            data = data[:, 0]
        audio_array = data
        if sr != expected_sample_rate:
            print(f"Warning: sample rate {sr} != {expected_sample_rate}. Proceeding without resample.")
    except Exception as e:
        print("Failed to load audio with soundfile, falling back to path for Whisper:", e)

    if audio_array is not None:
        res = model.transcribe(audio_array, task="transcribe", language="en")
    else:
        res = model.transcribe(audio_path, task="transcribe", language="en")
    text = res.get("text", "").strip()
    print(f"Transcription: {text}")
    
    # Clean up temporary file
    try:
        os.remove(audio_path)
    except Exception:
        pass
    
    return text, res