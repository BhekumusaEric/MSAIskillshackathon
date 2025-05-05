# SafeWayAI Deployment Guide

This guide provides instructions for deploying the SafeWayAI application in various environments.

## Local Deployment

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/BhekumusaEric/MSAIskillshackathon.git
   cd MSAIskillshackathon
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python wsgi.py
   ```

4. Access the application at http://127.0.0.1:8000

## Production Deployment

### Using Gunicorn (Recommended)

1. Install Gunicorn and Uvicorn:
   ```bash
   pip install gunicorn uvicorn
   ```

2. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
   ```

3. For convenience, you can use the provided deployment script:
   ```bash
   ./deploy.sh
   ```

### Deploying to Heroku

1. Create a Heroku account and install the Heroku CLI.

2. Login to Heroku:
   ```bash
   heroku login
   ```

3. Create a new Heroku app:
   ```bash
   heroku create safewayai
   ```

4. Push to Heroku:
   ```bash
   git push heroku main
   ```

5. The application will be available at the URL provided by Heroku.

## Configuration

### API Keys

Before deploying, make sure to set up your API keys:

1. Google Maps API key in `config/google_maps_config.json`
2. Firebase configuration in `config/firebase_key.json`

For security, it's recommended to use environment variables for sensitive information in production.

## Troubleshooting

If you encounter issues with the deployment:

1. Check the logs:
   ```bash
   heroku logs --tail
   ```

2. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify that the API keys are correctly configured.

## Support

For additional support, please open an issue on the GitHub repository.
