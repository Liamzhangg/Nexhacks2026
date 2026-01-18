from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import tempfile
import uuid


from langchain.agents import create_agent
from system_prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
import os
load_dotenv()
GOOGLE_API_KEY =os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"]= GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from video_script import run_video_workflow

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
    """Send the uploaded video + prompt to the Gemini agent for contextual text."""
    if not input_text:
        return ""

    with open(video_path, "rb") as video_file:
        video_base64 = base64.b64encode(video_file.read()).decode("utf-8")

    mime_type = "video/mp4"
    message = HumanMessage(
        content=[
            {"type": "text", "text": input_text},
            {"type": "video", "base64": video_base64, "mime_type": mime_type},
        ]
    )
    response = agent.invoke({"messages": [message]})
    return response["messages"][-1].content


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_video_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


DEFAULT_POSITIVE_PROMPT = "three pepsi cans spinning from above"
DEFAULT_SEGMENTATION_PROMPT = "coke bottle"


def process_video_backend(video_path, text_input, *, image_path=None):
    """
    Run the ComfyUI workflow (video_script.py) and return the generated file path + text output.
    """
    if not image_path or not os.path.exists(image_path):
        raise ValueError("A reference image is required to run the video workflow.")

    positive_prompt = text_input.strip() if text_input else DEFAULT_POSITIVE_PROMPT
    segmentation_prompt = text_input.strip() if text_input else DEFAULT_SEGMENTATION_PROMPT
    prefix = f"processed_{uuid.uuid4().hex}"

    generated_videos = run_video_workflow(
        video_path=video_path,
        positive_prompt=positive_prompt,
        reference_image=image_path,
        segmentation_prompt=segmentation_prompt,
        filename_prefix=prefix,
        additional_overrides={"queue_size": 1},
    )

    if not generated_videos:
        raise RuntimeError("Video generation workflow did not produce any outputs.")

    processed_video_path = os.path.abspath(generated_videos[0])
    if not os.path.exists(processed_video_path):
        raise FileNotFoundError(f"Generated video missing at {processed_video_path}")

    text_output = backend(video_path, text_input)
    return processed_video_path, text_output


@app.route('/process-video', methods=['POST'])
def process_video():
    """
    Endpoint to receive video and text from frontend,
    process it, and return the processed video
    """
    input_path = None
    image_path = None
    output_path = None
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        image_file = request.files.get('image')
        text_input = request.form.get('text', '')
        
        # Validate file
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        if not allowed_video_file(video_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        if image_file is None or image_file.filename == '':
            return jsonify({'error': 'Reference image is required'}), 400

        if not allowed_image_file(image_file.filename):
            return jsonify({'error': 'Invalid image file type'}), 400
        
        # Save uploaded video
        filename = secure_filename(video_file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(input_path)

        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image_file.save(image_path)
        
        # Process video with backend
        output_path, output_text = process_video_backend(
            input_path,
            text_input,
            image_path=image_path,
        )
        with open(output_path, 'rb') as processed_file:
            video_base64 = base64.b64encode(processed_file.read()).decode('utf-8')
        
        # Return processed video
        return jsonify({
            'video': video_base64,
            'text': output_text,
            'filename': os.path.basename(output_path)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up uploaded file
        for path in (input_path, image_path, output_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
