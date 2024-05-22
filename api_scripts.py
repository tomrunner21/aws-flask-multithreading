import threading
import requests
import pandas as pd
import time
import boto3
from botocore.exceptions import NoCredentialsError

# Your OpenAI API Key
API_KEY = 'your-openai-api-key'

# GPT-4 API endpoint
API_URL = "https://api.openai.com/v1/completions"

# Headers for API authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

def download_file_from_s3(bucket_name, file_key, local_file_name):
    """Download a file from S3 to a local file."""
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, file_key, local_file_name)
        print(f"Successfully downloaded {file_key} from S3 bucket {bucket_name}")
        return local_file_name
    except NoCredentialsError:
        print("Credentials not available")
        return None

def read_and_clean_data(filepath, column_name):
    df = pd.read_csv(filepath)
    df = df.dropna(subset=[column_name])
    df[column_name] = df[column_name].str.strip()
    return df[column_name].values.tolist()

def api_request(inputs):
    session = requests.Session()
    for input_text in inputs:
        data = {
            "model": "text-davinci-004",
            "prompt": f"Translate the following English text to French: '{input_text}'",
            "max_tokens": 60
        }
        response = session.post(API_URL, headers=headers, json=data)
        print(f"Response Code: {response.status_code}, Response Body: {response.json()}")

def main(bucket_name, file_key, column_name):
    local_file_name = download_file_from_s3(bucket_name, file_key, 'local.csv')
    if local_file_name:
        values = read_and_clean_data(local_file_name, column_name)
        chunk_size = len(values) // NUMBER_OF_THREADS
        threads = []
        start_time = time.time()

        for i in range(NUMBER_OF_THREADS):
            start_index = i * chunk_size
            end_index = None if i+1 == NUMBER_OF_THREADS else (i+1) * chunk_size
            thread = threading.Thread(target=api_request, args=(values[start_index:end_index],))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        print(f"Completed in {end_time - start_time} seconds.")

if __name__ == "__main__":
    bucket_name = 'your-bucket-name'  # AWS S3 bucket name
    file_key = 'your-file-key.csv'  # S3 object key
    column_name = 'your_column_name'  # Column to process
    main(bucket_name, file_key, column_name)
