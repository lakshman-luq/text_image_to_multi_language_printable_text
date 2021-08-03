from flask import Flask, render_template, request
import textblob
from text_speech import image_text
from textblob import TextBlob
from gtts import gTTS
import os, glob, boto3
from random import random
from io import BytesIO

app = Flask(__name__)

#allow flies of a specific extension
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'tif'])

bucket_name = os.environ.get('S3_BUCKET')
access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secrect_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key=secrect_key)
bucket = s3.Bucket(bucket_name)

def translate_text_speech(t, lang):
    tb = TextBlob(t)
    if lang == 'en':
        tr_txt = 'Please enter language code to get translation of the text.'
        txt_sp = gTTS(text=t, lang='en')
    else:
        tr_txt = str(tb.translate(to=lang))
        try:
            txt_sp = gTTS(text=tr_txt, lang=lang)
        except:
            txt = 'Hey, the language code, is not supported for speech generator, please enter another language code'
            txt_sp = gTTS(text=txt, lang='en')
    return tr_txt, txt_sp

#function to check the file extension 
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#route and function to handle the upload page
@app.route('/', methods=['GET', 'POST'])

def home_page():
    if request.method == 'POST':
        num = str(int(random()*1000))
        #check if there is a file in the request
        if 'file' not in request.files:
            return render_template('index.html', msg = 'No file selected')
        file = request.files['file']
        lang = str(request.form.get('text', False))
        if lang == '':
            return render_template('index.html', msg = 'Error: Please enter language code')
        #if no file is selected
        if file.filename == '':
            return render_template('index.html', msg = 'No file selected')
        
        if file and allowed_file(file.filename): 
            #call the ocr function on it
            extracted_text = image_text(file)
            translators = translate_text_speech(t=extracted_text, lang=lang)
            translate_text = translators[0]
            textSpeech = translators[1]
            #path = glob.glob('text_image_to_multi_language_printable_text/static/*.mp3')
            fileName = num+'_audio_'+lang+'.mp3'
            #textSpeech.save('text_image_to_multi_language_printable_text\\static\\'+ fileName)
            #for i in path:
            #    os.remove(i)
            audio_path = 'https://audio-file-mp3.s3.amazonaws.com/'+fileName
            #bucket.objects.delete()
            fp = BytesIO()
            textSpeech.write_to_fp(fp)
            fp.seek(0)
            bucket.objects.delete()
            bucket.upload_fileobj(fp, fileName)
            #extract the text and display it
            return render_template('index.html', 
                                   msg = 'Successfully processed', 
                                   extracted_text = extracted_text,
                                   translate_text = translate_text,
                                   audio_path = audio_path)

    elif request.method == 'GET':
        return render_template('index.html')

if __name__=='__main__':
    app.run(debug=True)
