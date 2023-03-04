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


    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    print("decoded into cv2")

    if img is None:
        print("img is none")

    # resize b/w image
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    print("resized")

    # convert to black and white
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    print("converted to b/w")

    # apply adaptive threshold
    img_bw = cv2.adaptiveThreshold(img_bw, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                            cv2.THRESH_BINARY_INV, 199, 25)

    print("applied adaptive threshold")

    # detect text with pytesseract with b/w image
    text = pytesseract.image_to_string(img_bw, config="--psm 6")

    print("detected text from image")

    split = text.splitlines()

    cleaned = []

    if debug:
        # extract bounding boxes from b/w image
        boxes = pytesseract.image_to_boxes(img_bw)
        print("extracted bounding boxes")

        img_color = img

        h, _, _ = img_color.shape

        # add bounding boxes to original color image
        for b in boxes.splitlines():
            b = b.split()
            cv2.rectangle(img_color, ((int(b[1]), h - int(b[2]))), ((int(b[3]), h - int(b[4]))), (0, 255, 0), 3)
        
        _, encoded_color = cv2.imencode('.jpg', img_color)
        img_bytes_color = encoded_color.tobytes()
        img_b64_color = str(base64.b64encode(img_bytes_color))[1:]
        _, encoded_bw = cv2.imencode('.jpg', img_bw)
        img_bytes_bw = encoded_bw.tobytes()
        img_b64_bw = str(base64.b64encode(img_bytes_bw))[1:]
        print("encoded back into base64")

    # clean the detected text
    for i in range(len(split)):
        if not split[i].isspace() and len(split[i]) > 0 and bool(set('0123456789').intersection(split[i])):
            cleaned.append(split[i])

    # build a response dict to send back to client
    if debug:
        response = {'status': 200, 'img_color': img_b64_color, 'img_bw': img_b64_bw, 'text': cleaned}
    else:
        response = {'status': 200, 'text': cleaned}

    print("done!")

    return response
