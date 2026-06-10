import whisper

print("Loading Whisper model...")

model = whisper.load_model("large-v3")

print("Transcribing audio...")

# result = model.transcribe("ai-pipeline/audio/video_Udara_Week1.mp4")
result = model.transcribe("ai-pipeline/audio/diabetes_audio_question.mp3")

print("\nTranscription:\n")
print(result["text"])