from __future__ import unicode_literals
import errno
import os
import sys
import tempfile
from dotenv import load_dotenv
from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, PostbackEvent, StickerMessage, StickerSendMessage,
    LocationMessage, LocationSendMessage, ImageMessage, ImageSendMessage
)
import time
from pathlib import Path
import cv2
import torch
from PIL import Image
from utils.plots import Annotator, colors
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import tensorflow as tf
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)
load_dotenv()

# Environment variables for LINE Bot
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
if channel_secret is None or channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Ensure the static temporary directory exists
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path, exist_ok=True)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

make_static_tmp_dir()

# YOLOv5 setup
weights, imgsz = 'Fold_FINAL.pt', 640

yolov5_model = None

# Try to load YOLOv5 model
try:
    yolov5_model = torch.hub.load('ultralytics/yolov5', 'custom', path='Fold_FINAL.pt', source='github')
except Exception as e:
    logger.error(f"Error loading YOLOv5 model: {e}")

# TensorFlow model for classification
classification_model_path = 'best_model_improved.keras'
try:
    classification_model = load_model(classification_model_path)
except Exception as e:
    logger.error(f"Error loading classification model: {e}")

# Class names mapping
class_names = {
    0: 'Coccidiosis', 1: 'Healthy', 2: 'Newcastle Disease', 3: 'Salmonella'
}

# Function to preprocess images for classification
def preprocess_image(img_path, target_size=(224, 224)):
    img = Image.open(img_path).convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img, dtype='float32') / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.route("/", methods=['GET'])
def home():
    return "Object Detection API"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error(f"Got exception from LINE Messaging API: {e.message}")
        for m in e.error.details:
            logger.error(f"  {m.property}: {m.message}")
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    if text == 'profile' and isinstance(event.source, SourceUser):
        profile = line_bot_api.get_profile(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='Display name: ' + profile.display_name)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Bot can't use profile API without user ID")
            if text == 'profile' else TextSendMessage(text=text)
        )

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token, LocationSendMessage(
            title='Location', address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token, StickerSendMessage(
            package_id=event.message.package_id, sticker_id=event.message.sticker_id
        )
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_content_message(event):
    # Inform the user that detection is starting
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text="Please wait, we are detecting! 🕵️‍♂️")
    )

    # Get the image from the message content
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='jpg-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.jpg'
    os.rename(tempfile_path, dist_path)
    im = cv2.imread(dist_path)
    im0 = im.copy()
    results = yolov5_model(im, size=imgsz)

    if results.xyxy[0].shape[0] == 0:
        # No detections were made, send another message
        line_bot_api.push_message(
            event.source.user_id, TextSendMessage(text="Sorry, we cannot detect it. Please upload it again! 🐔")
        )
        return  # Stop further processing

    line_width = 6  # Adjust line width for bounding boxes
    annotator = Annotator(im0, line_width=line_width)
    full_result_text = "Detection Results 🐣\n"

    for *xyxy, conf, cls in results.xyxy[0]:
        x0, y0, x1, y1 = map(int, xyxy)
        crop_img = im0[y0:y1, x0:x1]

        if crop_img.size == 0:
            # No valid crop could be made
            continue  # Skip this detection

        crop_file = f'crop_{int(time.time())}.jpg'
        cv2.imwrite(crop_file, crop_img)
        preprocessed_img = preprocess_image(crop_file)
        predictions = classification_model.predict(preprocessed_img)
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        predicted_class_name = class_names[predicted_class_index]
        predicted_label = f'{predicted_class_name}: {np.max(predictions) * 100:.2f}%'
        predicted_label2 = f'{predicted_class_name}\nConfidence {np.max(predictions) * 100:.2f}%'
        annotator.box_label(xyxy, predicted_label, color=colors(int(cls), True))
        full_result_text += f"\n{predicted_label2}\n"
        full_result_text += "\n"

    save_path = str(Path('static/tmp') / f'{Path(tempfile_path).stem}_result.jpg')
    cv2.imwrite(save_path, im0)
    url = request.url_root + '/' + save_path

    # Use push_message to send the detection results after initial acknowledgment
    line_bot_api.push_message(
        event.source.user_id, [
            TextSendMessage(text=full_result_text.strip()),
            ImageSendMessage(original_content_url=url, preview_image_url=url)
        ])


@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
