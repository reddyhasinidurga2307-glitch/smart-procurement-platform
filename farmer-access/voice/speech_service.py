import os
import tempfile

import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr


def record_audio(sample_rate=44100):

    print()
    input("Press Enter to START recording...")

    print("Listening... Speak now.")
    print("Press Enter when you finish speaking.")

    recording = []

    def callback(indata, frames, time, status):

        if status:
            print("Audio status:", status)

        recording.append(indata.copy())

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        callback=callback
    ):

        input()

    print("Recording stopped.")

    if not recording:

        return None

    audio_data = np.concatenate(recording, axis=0)

    audio_level = np.max(np.abs(audio_data))

    print("Audio level:", round(float(audio_level), 4))

    if audio_level < 0.001:

        print("No clear microphone audio was detected.")

        return None

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    temp_file.close()

    sf.write(
        temp_file.name,
        audio_data,
        sample_rate
    )

    return temp_file.name


def listen_to_farmer():

    recognizer = sr.Recognizer()

    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    audio_file = None

    try:

        audio_file = record_audio()

        if audio_file is None:

            return {
                "success": False,
                "message": "No clear audio was recorded. Please check your microphone and try again."
            }

        with sr.AudioFile(audio_file) as source:

            audio = recognizer.record(source)

        print("Converting speech to text...")

        message = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("You said:", message)

        return {
            "success": True,
            "message": message
        }

    except sr.UnknownValueError:

        return {
            "success": False,
            "message": "I could hear the audio, but I could not understand the words. Please speak more clearly."
        }

    except sr.RequestError as error:

        return {
            "success": False,
            "message": f"Speech recognition service error: {error}"
        }

    except Exception as error:

        return {
            "success": False,
            "message": f"Voice system error: {error}"
        }

    finally:

        if audio_file and os.path.exists(audio_file):

            try:
                os.remove(audio_file)
            except OSError:
                pass


if __name__ == "__main__":

    result = listen_to_farmer()

    print()
    print(result)