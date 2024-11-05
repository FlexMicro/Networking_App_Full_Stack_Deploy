from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this import
from werkzeug.utils import secure_filename
import boto3
import os
from botocore.exceptions import ClientError
import uuid
from boto3.session import Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create a session with your specific profile
session = Session(profile_name='flex-admin')  # Replace 'myenv' with your profile name

# Create S3 client using the session
s3_client = session.client('s3')

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
S3_BUCKET = os.getenv('S3_BUCKET')  # You can still keep bucket name in env var if desired

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Check file size
    file_content = file.read()
    if len(file_content) > MAX_FILE_SIZE:
        return jsonify({'error': 'File size exceeds limit'}), 400
    
    file.seek(0)  # Reset file pointer after reading
    
    try:
        # Generate unique filename with a folder structure based on date
        filename = secure_filename(file.filename)
        unique_filename = f"uploads/{uuid.uuid4()}_{filename}"
        
        # Upload to S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            unique_filename,
            ExtraArgs={
                'ContentType': file.content_type
            }
        )
        
        # Get the region from the s3 client
        region = s3_client.meta.region_name
        
        # Generate the URL of the uploaded file
        file_url = f"https://{S3_BUCKET}.s3.{region}.amazonaws.com/{unique_filename}"
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': unique_filename,
            'url': file_url
        }), 200
        
    except ClientError as e:
        app.logger.error(f"Error uploading to S3: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    # Add startup checks
    if not S3_BUCKET:
        raise ValueError("S3_BUCKET environment variable must be set")
    
    # Verify credentials at startup
    try:
        s3_client.list_buckets()
        print(f"Successfully connected to AWS using profile: {session.profile_name}")
        print(f"Using region: {s3_client.meta.region_name}")
    except Exception as e:
        print(f"Error verifying AWS credentials: {str(e)}")
        raise
    
    app.run(debug=True)