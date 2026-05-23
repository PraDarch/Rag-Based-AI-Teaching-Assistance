import pandas as pd 
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np 
import joblib 
import requests
import os

DB_PATH = 'embeddings.joblib'
OLLAMA_URL = "http://localhost:11434"

def check_ollama_status():
    try:
        r = requests.get(OLLAMA_URL, timeout=2)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def create_embedding(text_list):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/embed", json={
            "model": "bge-m3",
            "input": text_list
        }, timeout=15)
        if r.status_code != 200:
            raise Exception(f"Ollama embedding failed (Status {r.status_code}): {r.text}")
        return r.json()["embeddings"]
    except requests.exceptions.ConnectionError:
        raise Exception(f"Ollama offline. Ensure Ollama is running at {OLLAMA_URL}.")

def inference(prompt):
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }, timeout=60)
        if r.status_code != 200:
            raise Exception(f"Ollama generation failed (Status {r.status_code}): {r.text}")
        return r.json()
    except requests.exceptions.ConnectionError:
        raise Exception(f"Ollama offline. Ensure Ollama is running at {OLLAMA_URL}.")

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def main():
    print("="*80)
    print("🎓  RAG-BASED AI TEACHING ASSISTANT (CLI Console Mode)")
    print("="*80)

    # 1. Verify Database file
    if not os.path.exists(DB_PATH):
        print(f"\n[ERROR] Database file '{DB_PATH}' was not found.")
        print("Please run 'python preprocess_json.py' first to vectorize your course transcripts.\n")
        return

    # 2. Verify Ollama Connection
    if not check_ollama_status():
        print(f"\n[ERROR] Failed to connect to local Ollama API at {OLLAMA_URL}.")
        print("Please verify that the Ollama app is running locally.\n")
        return

    print(f"Loading vector database from '{DB_PATH}'...")
    try:
        df = joblib.load(DB_PATH)
        print(f"Database loaded successfully. Total segments indexed: {len(df)}")
    except Exception as e:
        print(f"Error loading {DB_PATH}: {e}")
        return

    incoming_query = input("\nAsk a Question about the course: ")
    if not incoming_query.strip():
        print("Empty query. Exiting.")
        return

    print("Analyzing query & retrieving relevant course segments...")
    try:
        question_embedding = create_embedding([incoming_query])[0]
        
        # Calculate Cosine Similarities
        similarities = cosine_similarity(np.vstack(df['embedding']), [question_embedding]).flatten()
        
        top_results = 5
        max_indx = similarities.argsort()[::-1][0:top_results]
        new_df = df.loc[max_indx] 
        
        print("\n--- [TOP RETRIEVED REFERENCE CHUNKS] ---")
        for idx, row in new_df.iterrows():
            time_start = format_time(row['start'])
            time_end = format_time(row['end'])
            print(f"- Video #{row['number']} '{row['title']}' [{time_start} - {time_end}]: \"{row['text'].strip()}\"")
        print("-" * 40)
        
        prompt = f'''I am teaching web development in my Sigma web development course. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

{new_df[["title", "number", "start", "end", "text"]].to_json(orient="records")}
---------------------------------
"{incoming_query}"
User asked this question related to the video chunks, you have to answer in a human way (dont mention the above format, its just for you) where and how much content is taught in which video (in which video and at what timestamp) and guide the user to go to that particular video. If user asks unrelated question, tell him that you can only answer questions related to the course.
'''
        with open("prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt)
            print("\nSaved constructed RAG prompt template to 'prompt.txt'.")

        print("Querying Llama 3.2 locally...")
        response_data = inference(prompt)
        response = response_data.get("response", "")
        
        print("\n=== [🎓 TEACHING ASSISTANT ANSWER] ===")
        print(response)
        print("="*40)
        
        with open("response.txt", "w", encoding="utf-8") as f:
            f.write(response)
            print("\nSaved generated response to 'response.txt'.")
            
    except Exception as e:
        print(f"\n[ERROR] Operation failed: {e}\n")

if __name__ == "__main__":
    main()