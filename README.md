# 🐔 ChickenME 🐣: Classification of Chicken Diseases From Fecal Images Via Line Office Account

## Overview
This repository contains the code for the **ChickenME** project, a mobile-based tool designed to assist local farmers in identifying common poultry diseases through the analysis of fecal images. By leveraging machine learning models, the system classifies chicken diseases and offers preliminary diagnoses via a user-friendly interface integrated into a LINE official account.

The project achieved **86.49% segmentation mean average precision** and **95.93% classification accuracy** using a comprehensive open database. ChickenME provides a cost-effective alternative to traditional diagnostic methods, distinguishing between diseased and healthy samples, helping farmers make informed decisions about poultry health.

**Publication**: Accepted at IEEE Region 10 Conference 2024 (TENCON 2024) under the title *Practical Mobile Based Services for Identification of Chicken Diseases From Fecal Images*.

### Key Contributors:
- **Developed by**: Waris Damkham, Pattanan Korkiattrakool
- **Advisor**: Asst. Prof. Dr. Piyanuch Silapachote
- **Co-Advisor**: Asst. Prof. Dr. Ananta Srisuphab
- **Institution**: Mahidol University, Faculty of Information and Communication Technology

---

## Setup Instructions

### 1. Environment Setup
To run the project, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Waariss/Chicken_Me-LineOA.git
   cd Chicken_Me-LineOA
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** and set up the following environment variables:
   ```
   LINE_CHANNEL_SECRET='<Your_Line_Channel_Secret>'
   LINE_CHANNEL_ACCESS_TOKEN='<Your_Line_Channel_Access_Token>'
   ```

4. **Run the server**:
   ```bash
   python line_up_fix.py
   ```

### 2. Docker Setup (Optional)
You can also run the project using Docker. Use the following command to pull the Docker image and run it:

```bash
docker pull waaris/line
docker run -p 8000:8000 -e LINE_CHANNEL_SECRET='<Your_Line_Channel_Secret>' -e LINE_CHANNEL_ACCESS_TOKEN='<Your_Line_Channel_Access_Token>' waaris/line:latest
```
### 3. Downloading the Pre-trained Model
The pre-trained models for both object detection and classification are required. You can download the models from [Google Drive](https://drive.google.com/drive/folders/1FlIJu6P79gaXv6O37tYnRBv-afmvCCm-?usp=sharing) and place them in the appropriate directories.

- YOLOv5 model: `Fold_FINAL.pt`
- TensorFlow classification model: `best_model_improved.keras`

### 4. Webhook Setup
Once the server is running, you will need to set up the webhook in the Line Developers Console:

- Go to the **Line Developers Console**.
- In the **Messaging API** section, configure the **Webhook** settings.
- Set the **Webhook URL** to point to your server (or use **Ngrok** for local testing).
- Enable the **Use Webhook** option.

To test locally, you can use **Ngrok** to expose your server to the internet:
```bash
ngrok http 8000
```

## How It Works

1. **User Interaction**: Users interact with the Line bot by sending images of chicken feces. The bot processes these images and returns the results (disease classification).
   
2. **Webhook**: The Line bot uses a Flask server to handle incoming requests (messages) via a webhook. When an image is received, the server processes it using YOLOv5 for detection and a TensorFlow model for disease classification.

3. **Image Processing**:
   - The system first detects regions of interest using YOLOv5.
   - It then crops and preprocesses the detected regions.
   - The cropped regions are fed into the classification model to predict the disease.
   - The result is sent back to the user with a confidence score.

4. **Supported Diseases**:
   - Coccidiosis
   - Healthy
   - Newcastle Disease
   - Salmonella

## Code Summary

- **`line_up_fix.py`**: Main entry point for running the server.
- **Object Detection**: YOLOv5 is used for detecting regions of interest in the images.
- **Classification**: A pre-trained TensorFlow model classifies detected regions into specific chicken diseases.
- **Flask Server**: Handles incoming webhook requests from Line and processes image messages.
  
## Routes

- **`/`**: Health check route to ensure the server is running.
- **`/callback`**: Main webhook endpoint that handles incoming events such as messages from users.
  
## Contributing
Feel free to fork this repository, submit issues, or contribute pull requests.
