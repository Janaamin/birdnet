import os
import subprocess
import csv
from google.cloud import firestore, storage
from firebase_admin import credentials, initialize_app
from google.auth.transport.requests import Request
import google.auth

# Initialize Firebase Admin
cred = credentials.Certificate("firebase-key.json")
initialize_app(cred)

# Use google.auth to initialize Firestore Client
from google.cloud import firestore_v1
from google.auth import exceptions

# Get the default credentials and use them with Firestore
credentials, project = google.auth.load_credentials_from_file("firebase-key.json")
db = firestore_v1.Client(credentials=credentials, project=project)

storage_client = storage.Client()

def process_audio(bucket_name, file_name):
    """Process uploaded audio with BirdNET-Lite and save results to Firestore."""
    temp_file = f"/tmp/{file_name}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(temp_file)

    # Run BirdNET-Lite analysis
    output_csv = f"/tmp/result_{file_name}.csv"
    command = [
        "python3", "backend/BirdNET-Lite/analyze.py",
        "--i", temp_file,
        "--o", output_csv,
        "--lat", "35.4244",
        "--lon", "-120.7463",
        "--week", "48"
    ]
    subprocess.run(command, check=True)

    # Parse results and save to Firestore
    with open(output_csv, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            db.collection("birds").add({
                "bird": row["Species"],
                "confidence": float(row["Confidence"]),
                "start_time": float(row["Start (s)"]),
                "end_time": float(row["End (s)"]),
                "timestamp": firestore.SERVER_TIMESTAMP,
                "audio_file": file_name
            })

    # Clean up
    os.remove(temp_file)
    os.remove(output_csv)
