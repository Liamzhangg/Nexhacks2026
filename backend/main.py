from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import tempfile


from langchain.agents import create_agent
from system_prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
import os
load_dotenv()
GOOGLE_API_KEY =os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"]= GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=1.0,  # Gemini 3.0+ defaults to 1.0
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

agent= create_agent(
    model=model,
    system_prompt= SYSTEM_PROMPT,
)

import base64
from langchain.messages import HumanMessage
def backend(video_path, input_text):
    video_bytes = open(video_path, "rb").read()
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
    mime_type = "video/mp4"
    message = HumanMessage(
        content=[
            {"type": "text", "text": input_text},
            {
                "type": "video",
                "base64": video_base64,
                "mime_type": mime_type,
                },
                ]
                )
    output_path = os.path.join(
        app.config['UPLOAD_FOLDER'], 
        f"processed_{os.path.basename(video_path)}"
    )
    response = agent.invoke({"messages":[message]})
    text=response["messages"][-1].content
    return output_path, text


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_video_backend(video_path, text_input):
    """
    Send video and text to backend for processing
    This is a placeholder - replace with your actual backend logic
    
    Args:
        video_path: Path to the uploaded video file
        text_input: Text input from the frontend
    
    Returns:
        Path to the processed video file
    """
    # TODO: Implement your backend processing logic here
    # Example: Send to ML model, video processing service, etc.
    
    # For now, just return the same video (placeholder)
    output_path = os.path.join(
        app.config['UPLOAD_FOLDER'], 
        f"processed_{os.path.basename(video_path)}"
    )
    
    # Simulate processing - in reality, you'd do actual processing here
    # Example: model.process(video_path, text_input)
    # Example: requests.post('http://backend-service/process', ...)
    
    # Placeholder: just copy the file
    import shutil
    shutil.copy(video_path, output_path)
    
    return output_path


@app.route('/process-video', methods=['POST'])
def process_video():
    """
    Endpoint to receive video and text from frontend,
    process it, and return the processed video
    """
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        text_input = request.form.get('text', '')
        
        # Validate file
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save uploaded video
        filename = secure_filename(video_file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(input_path)
        
        # Process video with backend
        output_path, output_text = process_video_backend(input_path, text_input)
        video_base64 = base64.b64encode(output_path).decode('utf-8')
        
        # Return processed video
        return jsonify({
            'video': video_base64,
            'text': output_text,
            'filename': f'processed_{filename}'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)