import whisper

model = whisper.load_model("base")

def transcribe(audio_path):
    result = model.transcribe(audio_path)

    return {
        "text": result["text"],
        "language": result["language"]
    }

if __name__ == "__main__":
    audio_file = "sample.wav"

    output = transcribe(audio_file)

    print(output)