import cv2
import numpy as np
import requests

# Create a dummy image
img = np.zeros((100, 100, 3), dtype=np.uint8)
img[:, :] = (0, 0, 255) # Red image
cv2.imwrite("dummy.jpg", img)

url = "http://127.0.0.1:8000/api/cctv/reference_photo"
files = {'photo': ('dummy.jpg', open('dummy.jpg', 'rb'), 'image/jpeg')}
data = {'role': 'WITNESS'}

response = requests.post(url, files=files, data=data)
print(response.status_code)
print(response.text)
