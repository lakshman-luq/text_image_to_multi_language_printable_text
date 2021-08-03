import pytesseract
import numpy as np 
from PIL import Image
#pytesseract.pytesseract.tesseract_cmd = '/app/.heroku/python/lib/python3.9/site-packages/tesseract'

def image_text(image):
    img = np.asarray(Image.open(image))
    text = pytesseract.image_to_string(img)
    text = str(text).replace('\n', ' ')
    return text
