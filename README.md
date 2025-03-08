# TR Placement Package Predictor

A web application that predicts placement packages based on CGPA using a linear regression model.

## Overview

This application uses a simple linear regression model to predict the placement package a student might receive based on their CGPA. It features:

- User-friendly interface with modern design
- Real-time predictions
- Celebratory animations when predictions are made
- User counter that tracks total users and predictions
- Responsive design that works on mobile and desktop

## Technology Stack

- **Backend**: Flask (Python)
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
4. Render will automatically detect the configuration from `render.yaml`
5. Manual configuration (if needed):
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

## Important Notes

- The templates and static files must be in the root `/templates` and `/static` directories for Render deployment
- Make sure the Flask app is initialized with the proper template and static folder paths
- The counter data is stored in `user_counter.json` file at the application root

## Contributors

- Designed & Developed by Aman Sharma

## Model Details

The linear regression model follows the equation:
```
package = 0.55795197 * cgpa - 0.8961119222429126
```

This means that for each additional point in CGPA, the predicted placement package increases by approximately 0.56 LPA.

## License

MIT 