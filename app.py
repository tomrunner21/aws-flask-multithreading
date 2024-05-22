
from flask import Flask, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
import boto3

from api_scripts import read_and_clean_data, api_request
# from api_scripts import process_file_from_s3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        file_key = request.form['file_key']
        column_name = request.form['column_name']
        if file and file_key and column_name:
            filename = secure_filename(file.filename)
            local_file_path = os.path.join('/tmp', filename)
            file.save(local_file_path)

            # Upload to S3
            bucket_name = os.getenv('BUCKET_NAME', 'default-bucket-name')
            s3_client = boto3.client('s3')
            s3_client.upload_file(local_file_path, bucket_name, file_key)

            processed_data = read_and_clean_data(local_file_path, column_name)
            api_request(processed_data)

            os.remove(local_file_path)

            # Process the file
            # process_file_from_s3(bucket_name, file_key, column_name)

            return redirect(url_for('upload'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
