from flask import Flask, render_template, request, session
from werkzeug.utils import secure_filename
from colorthief import ColorThief
import os
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def get_color_palette(image_path, num_colors):
    color_thief = ColorThief(image_path)
    palette = color_thief.get_palette(color_count=num_colors, quality=1)
    return ['#{:02x}{:02x}{:02x}'.format(r, g, b) for r, g, b in palette]

def clear_upload_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
            
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        clear_upload_folder(app.config['UPLOAD_FOLDER'])
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Store the image path and color palette in the session
            session['image_path'] = filepath
            session['color_palette'] = get_color_palette(filepath, 6)

            return render_template('index.html', image_path=session.get('image_path'),
                                   color_palette=session.get('color_palette'))

    # Display the form and any existing data in the session
    return render_template('index.html', image_path=session.get('image_path'),
                           color_palette=session.get('color_palette'))

if __name__ == '__main__':
    app.run(debug=True)
