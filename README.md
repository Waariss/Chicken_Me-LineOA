# 🐔 ChickenME 🐣: Classification of Chicken Diseases From Fecal Images via LINE Official Account

## Overview
**ChickenME** is a mobile-based service that helps local farmers identify common poultry diseases by analyzing fecal images through a LINE official account. The system leverages machine learning models to classify diseases and provides initial diagnoses via an intuitive interface.

This project achieved **86.49% segmentation mean average precision** and **95.93% classification accuracy** using a comprehensive open database. ChickenME offers an accessible, cost-effective alternative to traditional diagnostic methods, empowering farmers to make better decisions regarding poultry health.

**Publication**: Accepted at IEEE Region 10 Conference 2024 (TENCON 2024) under the title *Practical Mobile Based Services for Identification of Chicken Diseases From Fecal Images*.

### Key Contributors:
- **Developed by**: Waris Damkham, Pattanan Korkiattrakool
- **Advisor**: Asst. Prof. Dr. Piyanuch Silapachote
- **Co-Advisor**: Asst. Prof. Dr. Ananta Srisuphab
- **Institution**: Mahidol University, Faculty of Information and Communication Technology

### Live Project
You can interact with the ChickenME project by adding the LINE account [here](https://liff.line.me/1645278921-kWRPP32q/?accountId=239mhqhy).

### Note
The GitHub repository and a detailed explanation of how to train the model will be made available soon (TBA).

## Application Architecture and Flow

This section explains how the **ChickenME** app works through two key diagrams: the Docker image structure and the overall app architecture.

### 1. Inside the Docker Image

![Docker Image](link-to-docker-image)

The first diagram shows the structure of the Docker image used in the **ChickenME** app. Here’s a breakdown:

- **YOLOv5 Model**: This is used for object detection, specifically identifying relevant parts of the fecal image.
- **ResNet50 Model**: This model is responsible for classifying detected objects, determining whether the chicken has a disease.
- **Requirements**: The image includes all the dependencies required to run the application, such as `Flask`, `Gunicorn`, `line-bot-sdk`, and various machine learning libraries (TensorFlow, PyTorch, etc.).
- **Dockerfile**: The Dockerfile automates the installation of dependencies and sets up the environment for running the Flask app with Gunicorn, exposing it on port `8000`.

The Docker image is responsible for:
1. Setting up the environment with Python 3.10, installing required system libraries, and Python dependencies.
2. Running the Flask app using Gunicorn as the application server to handle requests from LINE's API.

### 2. Application Overview

![Application Overview](link-to-application-overview)

The second diagram provides an overview of the entire application flow, from the user sending an image to receiving a diagnosis.

- **User Interaction**: Users interact with the app via the **LINE Official Account**. They send images of chicken feces, which are then processed by the app.
- **Image Detection and Classification**: The image is passed through two models:
  1. **YOLOv5 for Object Detection**: Detects specific regions of interest in the fecal image.
  2. **ResNet50 for Classification**: Classifies the detected regions to identify possible diseases.
- **Flask API**: The LINE API sends the image to the Flask backend hosted inside the Docker container. The backend loads the YOLOv5 and ResNet50 models, performs the detection and classification, and then sends the result back to the user via the LINE app.
- **Cloud Infrastructure**:
  - The app is hosted on **Amazon EC2** and uses **DuckDNS** for dynamic DNS services.
  - **Nginx** acts as a reverse proxy to manage traffic and secure the connection using **Let's Encrypt** with **Certbot** for automatic SSL certificate management.

By combining these elements, **ChickenME** provides a fast and reliable service for identifying common poultry diseases based on fecal images, making it easier for farmers to maintain the health of their chickens.

## Setup Instructions

### 1. Environment Setup

Follow these steps to run the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Waariss/Chicken_Me-LineOA.git
   cd Chicken_Me-LineOA
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** and set the following environment variables:
   ```
   LINE_CHANNEL_SECRET='<Your_Line_Channel_Secret>'
   LINE_CHANNEL_ACCESS_TOKEN='<Your_Line_Channel_Access_Token>'
   ```

4. **Run the server**:
   ```bash
   python line_up_fix.py
   ```

### 2. Docker Setup (Optional)

To run the project using Docker, use the following command to pull the Docker image and run it:

```bash
docker pull waaris/line
docker run -p 8000:8000 -e LINE_CHANNEL_SECRET='<Your_Line_Channel_Secret>' -e LINE_CHANNEL_ACCESS_TOKEN='<Your_Line_Channel_Access_Token>' waaris/line:latest
```

### 3. Downloading the Pre-trained Model

The project requires pre-trained models for both object detection and classification. Download the models from [Google Drive](https://drive.google.com/drive/folders/1FlIJu6P79gaXv6O37tYnRBv-afmvCCm-?usp=sharing) and place them in the appropriate directories:

- YOLOv5 model: `Fold_FINAL.pt`
- TensorFlow classification model: `best_model_improved.keras`

### 4. Webhook Setup

Once the server is running, set up the webhook in the Line Developers Console:

- Go to the **Line Developers Console**.
- Under **Messaging API**, configure the **Webhook** settings.
- Set the **Webhook URL** to your server (use **Ngrok** for local testing).
- Enable the **Use Webhook** option.

To test locally, use Ngrok to expose your server to the internet:
```bash
ngrok http 8000
```

## Nginx Configuration

If you're hosting the ChickenME app on a server and want to serve it over HTTPS using Nginx as a reverse proxy, follow these steps:

### 1. Install Nginx

Make sure Nginx is installed on your server:

```bash
sudo apt update
sudo apt install nginx
```

### 2. Install Certbot for SSL

Certbot is used to obtain free SSL certificates from Let's Encrypt. Install Certbot along with the Nginx plugin:

```bash
sudo apt install certbot python3-certbot-nginx
```

### 3. Configure Nginx for Reverse Proxy and HTTPS

Edit the default Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/default
```

Replace the content with the following configuration:

```nginx
# HTTPS server block
server {
    listen 443 ssl;
    server_name <YOUR_DOMAIN>;

    # SSL certificates managed by Certbot
    ssl_certificate /etc/letsencrypt/live/<YOUR_DOMAIN>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<YOUR_DOMAIN>/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Proxy settings to forward requests to the application
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP server block to redirect all traffic to HTTPS
server {
    listen 80;
    server_name chickenme.duckdns.org;

    # Redirect all HTTP requests to HTTPS
    if ($host = <YOUR_DOMAIN>) {
        return 301 https://$host$request_uri;
    }
}
```

### 4. Obtain SSL Certificates Using Certbot

Run the following command to obtain an SSL certificate for your domain:

```bash
sudo certbot --nginx -d chickenme.duckdns.org
```

Follow the prompts to complete the SSL setup. Certbot will automatically configure SSL certificates for your Nginx server.

### 5. Verify Nginx Configuration

Check if the Nginx configuration is valid:

```bash
sudo nginx -t
```

If no errors are reported, reload Nginx to apply the changes:

```bash
sudo systemctl reload nginx
```

## How It Works

1. **User Interaction**: Users interact with the LINE bot by sending fecal images. The bot processes the images and returns disease classification results.
   
2. **Webhook**: The LINE bot uses a Flask server to handle incoming requests via a webhook. When an image is received, the server processes it using YOLOv5 for object detection and a TensorFlow model for disease classification.

3. **Image Processing**:
   - **Detection**: YOLOv5 detects regions of interest in the image.
   - **Preprocessing**: Detected regions are cropped and preprocessed.
   - **Classification**: The cropped regions are passed to a TensorFlow model for disease classification.
   - **Response**: The bot responds to the user with the

 classification result and confidence score.

4. **Supported Diseases**:
   - Coccidiosis
   - Healthy
   - Newcastle Disease
   - Salmonella

## Code Summary

- **`line_up_fix.py`**: Main script for running the server.
- **Object Detection**: YOLOv5 model detects regions of interest.
- **Classification**: Pre-trained TensorFlow model classifies diseases.
- **Flask Server**: Handles incoming webhook requests and processes image messages.

## Routes

- **`/`**: Health check route to verify the server is running.
- **`/callback`**: Webhook endpoint for processing incoming events such as user messages.

## Contributing

Feel free to fork this repository, open issues, or contribute via pull requests.
