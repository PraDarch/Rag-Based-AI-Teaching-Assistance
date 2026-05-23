import os
import json

# Ensure necessary directories exist
os.makedirs("audios", exist_ok=True)
os.makedirs("jsons", exist_ok=True)

audios = os.listdir("audios")
audios_to_process = []

# Check if the audios directory is completely empty
audio_files = [f for f in audios if f.lower().endswith('.mp3')]
if not audio_files:
    print("\n" + "="*80)
    print("WARNING: No audio files (.mp3) found in your 'audios/' directory!")
    print("Please place your video files in 'videos/' and run 'python video_to_mp3.py' first.")
    print("="*80 + "\n")
    raise SystemExit("Exiting because 'audios/' is empty.")

# Check which audio files actually need transcription
for audio in audio_files:
    # Gracefully parse audio number and title
    if "_" in audio:
        number = audio.split("_")[0]
        title = audio.split("_")[1][:-4]
    else:
        number = "00"
        title = audio[:-4]
        
    output_path = f"jsons/{audio}.json"
    if os.path.exists(output_path):
        print(f"Skipping {audio} -> JSON transcript already exists: {output_path}")
    else:
        audios_to_process.append((audio, number, title, output_path))

if not audios_to_process:
    print("All audio files in 'audios/' are already transcribed! No new Whisper processing needed.")
else:
    print(f"Found {len(audios_to_process)} audios to transcribe. Loading Whisper model large-v2...")
    import whisper
    model = whisper.load_model("large-v2")
    
    for audio, number, title, output_path in audios_to_process:
        print(f"Transcribing: {audio} (Tutorial {number} - {title})")
        try:
            result = model.transcribe(
                audio=f"audios/{audio}",
                language="hi",
                task="translate",
                word_timestamps=False
            )
            
            chunks = []
            for segment in result["segments"]:
                chunks.append({
                    "number": number,
                    "title": title,
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                })
            
            chunks_with_metadata = {"chunks": chunks, "text": result["text"]}
            
            with open(output_path, "w") as f:
                json.dump(chunks_with_metadata, f, indent=4)
            print(f"Saved transcript to: {output_path}")
        except Exception as e:
            print(f"Error transcribing {audio}: {e}")