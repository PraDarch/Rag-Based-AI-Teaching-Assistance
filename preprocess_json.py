import requests
import os
import json
import numpy as np
import pandas as pd
import joblib

DB_PATH = 'embeddings.joblib'

def check_ollama_status():
    try:
        r = requests.get("http://localhost:11434/")
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def create_embedding(text_list):
    # https://github.com/ollama/ollama/blob/main/docs/api.md#generate-embeddings
    try:
        r = requests.post("http://localhost:11434/api/embed", json={
            "model": "bge-m3",
            "input": text_list
        }, timeout=30)
        
        if r.status_code != 200:
            raise Exception(f"Ollama returned status {r.status_code}: {r.text}")
            
        embedding = r.json()["embeddings"] 
        return embedding
    except requests.exceptions.Timeout:
        raise Exception("Ollama connection timed out. Please check if your system is overloaded.")
    except requests.exceptions.ConnectionError:
        raise Exception("Failed to connect to Ollama server. Please ensure Ollama is running at http://localhost:11434.")

# Ensure jsons directory exists
os.makedirs("jsons", exist_ok=True)

# Load existing database if it exists
if os.path.exists(DB_PATH):
    print(f"Loading existing embeddings database from {DB_PATH}...")
    try:
        df_existing = joblib.load(DB_PATH)
        existing_titles = set(df_existing['title'].unique()) if 'title' in df_existing.columns else set()
        chunk_id = df_existing['chunk_id'].max() + 1 if 'chunk_id' in df_existing.columns else 0
        print(f"Database loaded. Found {len(df_existing)} existing chunks across {len(existing_titles)} videos.")
    except Exception as e:
        print(f"Error loading {DB_PATH}: {e}. Initializing a new database.")
        df_existing = pd.DataFrame()
        existing_titles = set()
        chunk_id = 0
else:
    print("No existing embeddings database found. Initializing a new one.")
    df_existing = pd.DataFrame()
    existing_titles = set()
    chunk_id = 0

jsons = os.listdir("jsons")
my_dicts = []
new_videos_count = 0

# Check Ollama health before starting
if jsons:
    # Filter files first
    jsons_to_process = []
    for json_file in jsons:
        if not json_file.lower().endswith('.json'):
            continue
            
        with open(f"jsons/{json_file}", "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                if not content.get("chunks"):
                    continue
                # Use the title of the first chunk to check if already in DB
                sample_title = content["chunks"][0].get("title", "")
                if sample_title in existing_titles:
                    print(f"Skipping {json_file} -> Video '{sample_title}' is already indexed.")
                else:
                    jsons_to_process.append((json_file, content, sample_title))
            except Exception as e:
                print(f"Error reading JSON file {json_file}: {e}")
                
    if jsons_to_process:
        if not check_ollama_status():
            print("\n" + "="*80)
            print("WARNING: Ollama server is offline! Please start Ollama before proceeding.")
            print("Make sure you run: 'ollama run bge-m3' in a terminal.")
            print("="*80 + "\n")
            raise SystemExit("Ollama is not running. Terminating indexing script.")
            
        for json_file, content, title in jsons_to_process:
            print(f"Creating Embeddings for {json_file} ('{title}') - Chunks: {len(content['chunks'])}")
            
            try:
                # Get embeddings in a single batch request
                texts = [c['text'] for c in content['chunks']]
                embeddings = create_embedding(texts)
                   
                for i, chunk in enumerate(content['chunks']):
                    chunk['chunk_id'] = chunk_id
                    chunk['embedding'] = embeddings[i]
                    chunk_id += 1
                    my_dicts.append(chunk)
                new_videos_count += 1
            except Exception as e:
                print(f"Error vectorizing chunks for {json_file}: {e}")

if my_dicts:
    df_new = pd.DataFrame.from_records(my_dicts)
    if not df_existing.empty:
        # Concatenate old and new
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
        
    joblib.dump(df_combined, DB_PATH)
    print(f"\nSuccessfully vectorized {new_videos_count} new video(s) and saved database to {DB_PATH}.")
    print(f"Total database now contains {len(df_combined)} chunks.")
else:
    print("\nDatabase is fully up to date! No new vector indexing required.")


