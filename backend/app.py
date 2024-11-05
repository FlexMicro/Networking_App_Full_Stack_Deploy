from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os
import logging
from werkzeug.utils import secure_filename
import redis
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize S3 client
try:
    s3 = boto3.client('s3')
except Exception as e:
    logger.error(f"Failed to initialize S3 client: {str(e)}")
    raise

# Initialize Redis client
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0)
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {str(e)}")
    raise

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        filename = secure_filename(file.filename)
        
        # Check if S3 bucket is configured
        bucket_name = os.getenv('S3_BUCKET')
        if not bucket_name:
            logger.error("S3_BUCKET environment variable not set")
            return jsonify({'error': 'Server configuration error'}), 500

        try:
            s3.upload_fileobj(
                file,
                bucket_name,
                filename,
                ExtraArgs={'ACL': 'public-read'}
            )
            
            file_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
            redis_client.lpush('recent_uploads', file_url)
            
            logger.info(f"Successfully uploaded file: {filename}")
            return jsonify({
                'message': 'File uploaded successfully',
                'url': file_url
            })
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            return jsonify({'error': 'Failed to upload to S3'}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/recent-uploads', methods=['GET'])
def get_recent_uploads():
    try:
        uploads = redis_client.lrange('recent_uploads', 0, -1)
        return jsonify({'uploads': [url.decode('utf-8') for url in uploads]})
    except Exception as e:
        logger.error(f"Error fetching recent uploads: {str(e)}")
        return jsonify({'error': 'Failed to fetch recent uploads'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')