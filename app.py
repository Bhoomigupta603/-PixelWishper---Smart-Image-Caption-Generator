from flask import Flask, render_template, request, redirect, url_for
from model.distillbert_caption import generate_caption
from werkzeug.utils import secure_filename
import os
import requests 
from gtts import gTTS
from PIL import Image
from io import BytesIO
import base64
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    caption = ""
    image_path = ""
    voice_filename = None
    
    if request.method == 'POST':
        image_file = request.files.get('image_file')
        image_url = request.form.get('image_url')
        paste_data = request.form.get('paste_data')
        webcam_data = request.form.get('webcam_data')

        
        # 1. File Upload
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(image_path)
            
            
        # URL Upload       
        elif image_url and image_url.strip() != '':
            try:
                import requests
                from PIL import Image
                from io import BytesIO
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content)).convert("RGB")
                filename = os.path.basename(image_url)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                img.save(image_path)
                
            except:
                return "Invalid image URL!" 
            
                   
         # 3. Pasted Image
        elif paste_data and paste_data.startswith('data:image/png;base64,'):
            image_bytes = base64.b64decode(paste_data.split(',')[1])
            img = Image.open(BytesIO(image_bytes))
            filename = f"{uuid.uuid4()}.png"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            img.save(image_path)    

        
         # 4. Webcam    
        elif webcam_data and webcam_data.startswith('data:image/png;base64,'):
            import base64
            from io import BytesIO
            from PIL import Image
            import uuid
            
            image_data = webcam_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            filename = f"{uuid.uuid4()}.png"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
    

        # Generate caption and voice
        if image_path:
            caption = generate_caption(image_path)
            tts = gTTS(caption)
            import uuid
            voice_filename = f"voice_{uuid.uuid4()}.mp3"
            tts.save(f"static/{voice_filename}")

    
    return render_template('index.html', caption=caption, image_path=image_path, voice_file=voice_filename)


if __name__ == '__main__':
    app.run(debug=True)
