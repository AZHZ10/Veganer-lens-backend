from flask import Flask, jsonify
from flask_cors import CORS
from lens import VeganerOCR

app = Flask(__name__)
CORS(app)

lens_ocr = VeganerOCR()

@app.route('/ocr', methods = ['GET'])
def readMenu():
    menuinfo = lens_ocr.send_info()
    return jsonify(menuinfo)

@app.route('/hello', methods = ['GET'])
def say_hello_world():
    #test
    return {'result': "Hello World"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = '5000', debug = True)
