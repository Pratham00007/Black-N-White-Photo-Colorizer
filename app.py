from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
from colorization import colorize_image

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
RESULT_FOLDER = 'static/results/'
SAMPLE_FOLDER = 'static/samples/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Get image paths from URL parameters (passed after processing)
    input_image = request.args.get('input_image')
    output_image = request.args.get('output_image')

    if request.method == 'POST':
        file = request.files.get('image')

        if file and file.filename != '':
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            output_path = os.path.join(app.config['RESULT_FOLDER'], file.filename)

            file.save(input_path)
            colorize_image(input_path, output_path)

            # Redirect to GET to show results (prevents form resubmission on refresh)
            return redirect(url_for('index', input_image=input_path, output_image=output_path))

    return render_template('index.html',
                           input_image=input_image,
                           output_image=output_image)


@app.route('/use-sample', methods=['POST'])
def use_sample():
    # This matches the 'name' attribute in the hidden HTML form
    filename = request.form.get('sample_filename')
    
    if filename:
        sample_path = os.path.join(SAMPLE_FOLDER, filename)
        # We copy it to uploads so it's treated like a user upload
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], "sample_" + filename)
        output_path = os.path.join(app.config['RESULT_FOLDER'], "sample_" + filename)

        # Copy the sample file to the upload folder first
        shutil.copy(sample_path, input_path)
        
        # Colorize
        colorize_image(input_path, output_path)

        return redirect(url_for('index', input_image=input_path, output_image=output_path))
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)