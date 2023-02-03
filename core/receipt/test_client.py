from __future__ import print_function
import requests
import json
import cv2
import base64
import io
import numpy as np
from PIL import Image

addr = 'http://127.0.0.1:5000'
test_url = addr + '/api/receipt'

# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}

img = cv2.imread('rc.jpg')
# encode image as jpeg
_, img_encoded = cv2.imencode('.jpg', img)

# send http request with image and receive response
response = requests.post(test_url, data=img_encoded.tobytes(), headers=headers).json()
# decode response

encoded_img = response['img'][1:]

print(encoded_img[:20])

decoded = base64.b64decode(encoded_img)

with open('test.jpg', 'wb') as f_output:
    f_output.write(decoded)

# expected output: {u'message': u'image received. size=124x124'}