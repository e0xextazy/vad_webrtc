import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from vad import Vad

UPLOAD_FOLDER = '.'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 60 * 8000 * 16

ALLOWED_EXTENSIONS = set(['wav', 'WAV'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/ready')
def ready():
    return 'OK'

@app.route('/recognize', methods=['POST'])
def upload_file():
    if 'wav' not in request.files:
        resp = jsonify({'message': 'No WAV part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['wav']
    if file.filename == '':
        resp = jsonify({'message': 'No WAV file provided for upload'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_folder = ''
        file.save(os.path.join(
            app.config['UPLOAD_FOLDER']+unique_folder, filename))
        vdata = {"vad": Vad(os.path.join(
            app.config['UPLOAD_FOLDER'], filename))}
        resp = jsonify(vdata)
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are wav, json'})
        resp.status_code = 400
        return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001)
