# test_s3.py
import unittest
from moto import mock_s3
import boto3
from app import s3_client, BUCKET_NAME

class TestS3Interaction(unittest.TestCase):
    @mock_s3
    def setUp(self):
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.s3.create_bucket(Bucket=BUCKET_NAME)

    @mock_s3
    def test_s3_upload(self):
        # Testing the upload functionality
        filename = 'test.txt'
        content = 'content'
        with open(filename, 'w') as f:
            f.write(content)

        # Call the S3 upload function
        s3_client.upload_file(filename, BUCKET_NAME, filename)

        # Check if the file exists in the bucket
        response = self.s3.list_objects(Bucket=BUCKET_NAME)
        self.assertIn('Contents', response)
        self.assertEqual(response['Contents'][0]['Key'], filename)
        
        # Clean up
        os.remove(filename)

if __name__ == '__main__':
    unittest.main()
