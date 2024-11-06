from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # En
# Configure upload folder
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_s3(local_file, bucket, s3_file):
    """
    Upload a file to an S3 bucket.
    
    :param local_file: Path to the local file
    :param bucket: S3 bucket name
    :param s3_file: S3 object name
    :return: True if file was uploaded, else False
    """
    s3_client = boto3.client('s3')
    
    try:
        s3_client.upload_file(local_file, bucket, s3_file)
        return True, "Upload Successful"
    except FileNotFoundError:
        return False, "File not found"
    except NoCredentialsError:
        return False, "AWS credentials not available"
    except Exception as e:
        return False, str(e)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Save file temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Upload to S3
        bucket_name = "mytest274984"
        success, message = upload_to_s3(temp_path, bucket_name, filename)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        if success:
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'bucket': bucket_name,
                's3_path': f's3://{bucket_name}/{filename}'
            }), 200
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)