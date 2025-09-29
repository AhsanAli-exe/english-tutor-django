# utils/audio_utils.py
import sounddevice as sd
import soundfile as sf
import tempfile
import queue
import threading
import numpy as np
import time
import os

def _record_worker(q, sample_rate, channels, stop_event):
    """
    Background worker that pushes numpy frames into a queue until stop_event is set.
    """
    def callback(indata, frames, time_info, status):
        # copy to avoid overwrite by PortAudio
        q.put(indata.copy())

    try:
        with sd.InputStream(samplerate=sample_rate, channels=channels, dtype='float32',
                            callback=callback):
            while not stop_event.is_set():
                time.sleep(0.05)
    except Exception as e:
        # push an exception placeholder so caller knows something failed
        q.put(("__ERROR__", str(e)))

def record_press_enter1(sample_rate=16000, channels=1):
    """
    CLI-friendly: Press ENTER to start recording, press ENTER again to stop.
    Returns: path to a WAV file (16-bit PCM) saved to a temp file.
    """
    print("\nPress ENTER to start recording (or Ctrl+C to cancel)...")
    try:
        input()
    except KeyboardInterrupt:
        print("Recording cancelled by user.")
        return None

    q = queue.Queue()
    stop_event = threading.Event()
    worker = threading.Thread(target=_record_worker, args=(q, sample_rate, channels, stop_event), daemon=True)
    worker.start()

    print("Recording... Press ENTER again to stop.")
    frames = []
    try:
        # Wait for Enter to stop recording
        input()
        # signal the worker to stop and give it a tiny moment
        stop_event.set()
        time.sleep(0.05)
    except KeyboardInterrupt:
        print("Interrupted by user while recording.")
        stop_event.set()

    # Drain queue
    while not q.empty():
        item = q.get()
        if isinstance(item, tuple) and item[0] == "__ERROR__":
            print("Audio device error:", item[1])
            return None
        frames.append(item)

    # concatenate frames
    if frames:
        audio = np.concatenate(frames, axis=0)
    else:
        audio = np.zeros((0, channels), dtype=np.float32)

    # Convert float32 [-1,1] -> int16
    # If audio is empty, create a 0.1s silent buffer to avoid empty-file issues
    if audio.shape[0] == 0:
        audio = np.zeros((int(0.1 * sample_rate), channels), dtype=np.float32)

    int16_audio = (audio * 32767).astype('int16')

    # write to temp WAV file
    tmpf = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    try:
        sf.write(tmpf.name, int16_audio, sample_rate, subtype='PCM_16')
    except Exception as e:
        print("Failed to write WAV file:", e)
        try:
            tmpf.close()
            os.unlink(tmpf.name)
        except:
            pass
        return None

    print("Recording saved to:", tmpf.name)
    return tmpf.name


# Keep your transcribe helper (copied and slightly hardened)
def transcribe_audio1(audio_path, model, expected_sample_rate=16000):
    """
    Transcribe using Whisper model instance (same behaviour as your original utils).
    Returns: (text, full_result_dict)
    """
    import soundfile as sf_local
    audio_array = None
    res = {}
    try:
        data, sr = sf_local.read(audio_path, dtype='float32')
        # Ensure mono
        if hasattr(data, 'ndim') and data.ndim == 2:
            data = data[:, 0]
        audio_array = data
        if sr != expected_sample_rate:
            print(f"Warning: sample rate {sr} != {expected_sample_rate}. Proceeding without resample.")
    except Exception as e:
        print("Failed to load audio with soundfile, falling back to path for Whisper:", e)

    try:
        if audio_array is not None:
            res = model.transcribe(audio_array, task="transcribe", language="en")
        else:
            res = model.transcribe(audio_path, task="transcribe", language="en")
    except Exception as e:
        print("Whisper transcription failed:", e)
        return "", {}

    text = res.get("text", "").strip()
    print(f"Transcription: {text}")

    # Clean up temp file where appropriate
    try:
        os.remove(audio_path)
    except Exception:
        pass

    return text, res
