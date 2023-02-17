from __future__ import print_function
import requests
import json
import cv2
import base64
import io
import numpy as np
from PIL import Image


img = cv2.imread('rc.jpg')
# encode image as jpeg
_, img_encoded = cv2.imencode('.jpg', img)

f = open("b64.txt", "a")
f.write(base64.b64encode(img_encoded).decode())
f.close()