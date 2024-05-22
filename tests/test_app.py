# test_app.py
from flask_testing import TestCase
from app import app
from unittest.mock import patch
import boto3
from moto import mock_s3

class TestFlaskApp(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    @mock_s3
    def setUp(self):
        self.conn = boto3.client('s3', region_name='us-east-1')
        self.conn.create_bucket(Bucket='your-bucket-name')

    # Test GET request to home page
    def test_home_page(self):
        response = self.client.get('/')
        self.assert200(response)
        self.assert_template_used('upload.html')

    # Test file upload handling
    @patch('app.process_file')  # Mocking the processing function
    def test_file_upload(self, mock_process_file):
        data = {
            'file': (io.BytesIO(b"test,data\n1,2"), 'test.csv'),
            'column_name': 'data'
        }
        response = self.client.post('/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        mock_process_file.assert_called_once_with('s3://your-bucket-name/test.csv', 'data')

    # Negative test for file upload without file part
    def test_upload_without_file(self):
        response = self.client.post('/', data={'column_name': 'data'})
        self.assert400(response)

if __name__ == '__main__':
    import unittest
    unittest.main()