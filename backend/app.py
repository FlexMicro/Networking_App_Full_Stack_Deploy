from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import NoCredentialsError
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_s3_client():
    """
    Create an S3 client using instance profile credentials
    """
    session = boto3.Session()
    return session.client('s3',
                         region_name='us-east-1')  # Replace with your region

def upload_to_s3(local_file, bucket, s3_file):
    """
    Upload a file to an S3 bucket using instance profile credentials
    """
    try:
        s3_client = get_s3_client()
        s3_client.upload_file(local_file, bucket, s3_file)
        # Get the public URL of the uploaded file
        location = s3_client.get_bucket_location(Bucket=bucket)['LocationConstraint']
        region = location if location else 'us-east-1'
        url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_file}"
        return True, "Upload Successful", url
    except NoCredentialsError:
        return False, "Could not find AWS credentials", None
    except Exception as e:
        return False, str(e), None

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        bucket_name = "mytest274984"
        success, message, url = upload_to_s3(temp_path, bucket_name, filename)
        
        os.remove(temp_path)
        
        if success:
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'bucket': bucket_name,
                's3_path': url
            }), 200
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)