# -*- coding: utf-8 -*-
"""510 milestone 2 backend.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_NHyDKFrkUPCrBHhz1NhcxmIauVy3W8U

## Backend Image Processing through Firebase Realtime Database

This script uses the Firebase Realtime Databse REST API to read an image from a database and write back the face detected in that image using OpenCV. To test the script, you can run it below and use [this web application](https://codepen.io/mayacakmak/pen/GwbvyZ/) that captures images from the camera and sends them to the database, and displays the detection on the image.

Before you run the code be sure to add [haarcascade_frontalface_default.xml](https://drive.google.com/file/d/1B_liy8IgGWpZvRgfWMd9ySeWEE-YuQQ8/view?usp=sharing) to your drive and change the link below accordingly.
"""

gray.shape



cv2_imshow(gray[:,::-1])

from google.colab import drive
drive.mount('/content/drive')

! pip install fer
from fer import FER
import matplotlib.pyplot as plt

import requests
import time
import json
import cv2
from PIL import Image
import io
import re
import base64
import numpy

from google.colab.patches import cv2_imshow

# Database info, **TODO** Update the information below to point to your database.
URL = "https://robot-app-50a41-default-rtdb.firebaseio.com/"

# For anonymous sign in, **TODO** Change the key below to be the API key of your Firebase project (Project Settings > Web API Key).
AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyBoDopRWPCT-h2CpbTQCmwUXTiG9zd_YRU";
headers = {'Content-type': 'application/json'}
auth_req_params = {"returnSecureToken":"true"}

# Start connection to Firebase and get anonymous authentication
connection = requests.Session()
connection.headers.update(headers)
auth_request = connection.post(url=AUTH_URL, params=auth_req_params)
auth_info = auth_request.json()
auth_params = {'auth': auth_info["idToken"]}

#print(auth_info)

def url_to_image(url):
  # imgstr = re.search(r'base64,(.*)', url).group(1)
  imgstr = url
  image_bytes = io.BytesIO(base64.b64decode(imgstr))
  im = Image.open(image_bytes)
  image = numpy.array(im)
  return image

while(True):

     # Sending get request and obtaining the image
  get_request = connection.get(url = URL + "image.json")
    # Extracting data in json format, this is a string representing the image
  image_str = get_request.json()
  # print(image_str)

    # Convert the image string into an actual image so we can process it
  image = url_to_image(str(image_str))

  # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  # Detect faces using the OpenCV functionality
  # faces = face_cascade.detectMultiScale(gray, 1.3, 5)
  # Get the results into an array we will send back to the database
 
  image2 = image[:,:,:3]

  #emotion 
  detector = FER(mtcnn=True)
  # print(detector.detect_emotions(img))
  # plt.imshow(img)
  result = detector.detect_emotions(image2)

  results = [];

  # create bounding box
  if result == []:
    print('please get back!')
    
    absent = {'warn':"I cannot see you, please get back!"}
    data_json =  json.dumps(absent)
    # The URL for the part of the database we will put the detection results
    detection_url = URL + "absent.json"
    # Post the data to the database
    post_request = connection.put(url=detection_url,
      data=data_json, params=auth_params)
    # Make sure data is successfully sent
    print("Detection data sent: " + str(post_request.ok))

    
  else:
    emotion, score = detector.top_emotion(image2)

    results.append({'x':result[0]["box"][0], 'y':result[0]["box"][1], 'w':result[0]["box"][2], 'h':result[0]["box"][3], 'emotion':emotion})
    
    print("Found " + str(len(results)) + " faces.")

    print(results)
  
    data_json =  json.dumps(results)
    detection_url = URL + "detection.json"
    post_request = connection.put(url=detection_url,
      data=data_json, params=auth_params)
    

    absent = {'warn':"You are here"}
    data_json2 =  json.dumps(absent)
    detection_url2 = URL + "absent.json"
    post_request2 = connection.put(url=detection_url2,
      data=data_json2, params=auth_params)

    print("Detection data sent: " + str(post_request.ok))
    print("Detection data sent: " + str(post_request2.ok))

  results = [];


  time.sleep(1)
