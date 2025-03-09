# TR Placement Package Predictor

A web application that predicts placement packages based on CGPA using a linear regression model.

## Overview

This application uses a simple linear regression model to predict the placement package a student might receive based on their CGPA. It features:

- User-friendly interface with modern design
- Real-time predictions
- Celebratory animations when predictions are made
- User counter that tracks total users and predictions
- Visitor tracking for analytics
- Feedback system for user comments
- Responsive design that works on mobile and desktop

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB Atlas (with fallback to file storage)
- **Frontend**: HTML, CSS, JavaScript
- **CSS Framework**: Bootstrap 4
- **Animations**: Canvas Confetti
- **Icons**: Font Awesome
- **Deployment**: Render

## Directory Structure

```
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   └── index.html         # Main page template
├── static/                # Static assets
│   └── style.css          # CSS styles
├── requirements.txt       # Python dependencies
├── render.yaml            # Render configuration
├── Procfile               # For Gunicorn
└── README.md              # Project documentation
```

## Local Development

1. Clone the repository:
```
git clone https://github.com/yourusername/tr-placement-calculator.git
cd tr-placement-calculator
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python app.py
```

4. Visit `http://127.0.0.1:5000/` in your browser.

## Deployment to Render

This application is configured for easy deployment on Render:

1. Push your code to a GitHub repository
2. In Render dashboard, create a new Web Service
3. Connect your GitHub repository
4. Set up the MongoDB connection:
   - Create a MongoDB Atlas account
   - Set up a free cluster
   - Create a database user
   - Get your connection string
   - Add it as the `MONGO_URI` environment variable in Render

## Features

### Prediction System
- Enter your CGPA and get an instant prediction
- Results are displayed with a celebration animation
- Based on a linear regression model

### User Tracking
- Tracks unique users with cookies
- Counts total predictions made
- Stores visitor data for analytics

### Feedback System
- Collects user feedback with a rating system
- Stores feedback in MongoDB for later review
- Includes name, email, message, and star rating

## Contributors

- Designed & Developed by Aman Sharma

## Model Details

The linear regression model follows the equation:
```