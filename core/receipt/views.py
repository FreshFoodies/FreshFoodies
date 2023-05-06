from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from . import receipt
import jsonpickle
import numpy as np
import cv2
import pytesseract
import re
import base64
import matplotlib.pyplot as plt
import json
import os

import pathlib
import subprocess

if os.name == 'nt':
    tesseract_path = str(pathlib.Path(__file__).parent.resolve()) + os.path.sep + 'Tesseract-OCR-Windows' + os.path.sep + 'tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

@receipt.route('/api/receipt', methods=['POST'])
def receipts():
    r = request

    debug = bool(r.headers.get("debug")) if r.headers.get("debug") else False

    print("trying to decode")
    decoded_data = base64.b64decode(r.data)

    print("base 64 decoded")

    nparr = np.frombuffer(decoded_data, np.uint8)

    img_bw = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    print("decoded into cv2")

    # resize b/w image
    img_bw = cv2.resize(img_bw, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # convert to black and white
    img_bw = cv2.cvtColor(img_bw, cv2.COLOR_BGR2GRAY)
    print("converted to b/w")

    img_bw = cv2.GaussianBlur(img_bw, (11, 11), cv2.BORDER_DEFAULT)
    print("blurred image")

    # apply adaptive threshold

    # detect text with pytesseract with b/w image
    # text = pytesseract.image_to_string(img_bw)
    text = pytesseract.image_to_string(img_bw)
    print("detected text from image")

    split = text.splitlines()

    cleaned = []

    # clean the detected text
    for i in range(len(split)):
        if not split[i].isspace() and len(split[i]) > 0 and bool(set('0123456789').intersection(split[i])):
            cleaned.append(split[i])

    print("cleaned text")

    _, encoded_bw = cv2.imencode('.jpg', img_bw)
    img_bytes_bw = encoded_bw.tobytes()
    img_b64_bw = str(base64.b64encode(img_bytes_bw))[1:]

    print("encoded back into base64")

    response = {'status': 200, 'text': cleaned}

    # build a response dict to send back to client
    if debug:
        response['img_bw'] = img_b64_bw

    print("done!")

    return response
