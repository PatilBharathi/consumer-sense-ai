Consumer Sense AI 🚀

Consumer Sense AI is an end-to-end analytics platform that transforms unstructured user feedback (App Store screenshots, tech blog URLs, and raw text) into actionable engineering strategy.

Built for the Google Cloud BNB Marathon 2025, it moves beyond simple sentiment analysis to act as an AI Product Manager, identifying specific UI bugs, hardware flaws, and feature requests using Gemini 2.5 Multimodal.

🌟 Key Features

Multimodal Ingestion:

📸 Visual Analysis: Uses Gemini 2.5 Flash to read UI screenshots directly, extracting usernames, ratings, and visual bugs.

🔗 Smart Web Scraper: Bypasses basic anti-bot measures to fetch product descriptions and reviews from URLs.

📝 Raw Text: Processes bulk feedback from support tickets or emails.

Strategic AI Logic:

Product Manager Persona: System prompts are designed to ignore generic noise and hunt for Pain Points and Feature Requests.

Smart Filtering: Automatically detects "ghost reviews" (empty/irrelevant text) and falls back to a SWOT analysis of the product description.

Serverless & Scalable:

Compute: Dockerized Streamlit app running on Cloud Run (scales to zero).

Storage: Hybrid architecture using Firestore (NoSQL App Data) and BigQuery (Analytics Warehouse).

🚀 Quick Start (Local Development)

1. Prerequisites

Python 3.10+

Google Cloud Project with Gemini API, Firestore, and BigQuery enabled.

Service Account Key (JSON) or API Key.

2. Environment Setup

Create a .env file in the root directory:

USE_REAL_GEMINI=true
GEMINI_API_KEY=your_google_ai_studio_key_here


3. Install Dependencies

pip install -r requirements.txt


4. Run the Application

Use the custom entry point to ensure imports work correctly:

# Windows
py -3.11 run.py

# Mac/Linux
python run.py


☁️ Deployment (Google Cloud Run)

We use Google Cloud Build to package the container and deploy it serverlessly.

1. Build Container

gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/consumer-sense-ai .


2. Deploy Service

gcloud run deploy consumer-sense-ai \
  --image gcr.io/YOUR_PROJECT_ID/consumer-sense-ai \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "USE_REAL_GEMINI=true,GEMINI_API_KEY=your_key" \
  --port 8080


📂 Project Structure

run.py: Entry point script that configures system paths before launching Streamlit.

app/: Main Streamlit UI application logic.

services/:

gemini_rest.py: Direct integration with Gemini 2.5 Flash/Pro APIs.

web_scraper.py: Robust scraper for fetching URL content.

workers/:

firestore_real.py: Handles NoSQL document storage.

bigquery_real.py: Handles analytics row insertion.

tests/: End-to-end pipeline tests.
