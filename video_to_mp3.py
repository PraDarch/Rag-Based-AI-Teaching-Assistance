# Converts the videos to mp3 
import os 
import subprocess

# Ensure necessary directories exist
os.makedirs("videos", exist_ok=True)
os.makedirs("audios", exist_ok=True)

files = os.listdir("videos")
if not files:
    print("No videos found in the 'videos/' directory. Please place your video files there.")
else:
    for file in files:
        if not file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm')):
            continue
            
        # Parse tutorial number and file name gracefully
        try:
            tutorial_number = file.split(" [")[0].split(" #")[1]
            file_name = file.split(" ｜ ")[0]
        except IndexError:
            # Fallback parsing if formatting differs from expectations
            base_name, _ = os.path.splitext(file)
            parts = base_name.split("_")
            if len(parts) >= 2 and parts[0].isdigit():
                tutorial_number = parts[0]
                file_name = "_".join(parts[1:])
            else:
                tutorial_number = "00"
                file_name = base_name
        
        output_file = f"audios/{tutorial_number}_{file_name}.mp3"
        
        # Incremental check: Skip conversion if the mp3 already exists
        if os.path.exists(output_file):
            print(f"Skipping {file} -> MP3 already exists: {output_file}")
            continue
            
        print(f"Converting: {file} -> {output_file}")
        try:
            subprocess.run([
                "ffmpeg", "-i", f"videos/{file}", 
                "-q:a", "0", "-map", "a", 
                output_file
            ], check=True)
        except Exception as e:
            print(f"Error converting {file}: {e}")