from flask import Flask, request, render_template, redirect, url_for
import boto3
import pandas as pd
import os

app = Flask(__name__)

# AWS S3 setup
s3_client = boto3.client('s3')
BUCKET_NAME = 'your-bucket-name'  # Update with your bucket name

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        column_name = request.form['column_name']
        if file and column_name:
            # Save the file to S3
            filename = file.filename
            file.save(filename)
            s3_client.upload_file(filename, BUCKET_NAME, filename)
            os.remove(filename)  # Remove the file after upload

            # Process the file
            file_path = f"s3://{BUCKET_NAME}/{filename}"
            process_file(file_path, column_name)
            return "File has been uploaded and processed"
    return render_template('upload.html')

def process_file(file_path, column_name):
    # Function to download, clean data and initiate API requests
    df = pd.read_csv(file_path)
    df = df.dropna(subset=[column_name])
    df[column_name] = df[column_name].str.strip()
    # Here you would add the function to pass data to your API
    print(df[column_name])

if __name__ == '__main__':
    app.run(debug=True)
