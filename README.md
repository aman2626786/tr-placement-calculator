# CGPA to Placement Package Predictor

A simple web application built with Flask that predicts placement packages (in LPA) based on CGPA using a linear regression model.

## Overview

This application implements a simple linear regression model that was trained on a dataset of student CGPA and their placement packages. The model predicts the likely placement package amount in Lakh Per Annum (LPA) based on a student's CGPA input.

## Features

- Input CGPA and get predicted placement package
- Clean and responsive UI built with Bootstrap
- Input validation for CGPA values
- Error handling

## Requirements

- Python 3.6+
- Flask 1.1.x
- MarkupSafe 2.0.1
- Gunicorn (for deployment)

## Local Setup

1. Clone the repository
```
git clone <repository-url>
cd cgpa-placement-predictor
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the application
```
python app.py
```

4. Open your browser and navigate to `http://127.0.0.1:5000/`

## Deployment to Render

This application can be easily deployed to Render:

1. Create a new Web Service on Render
2. Link to your Git repository
3. Set the build command to `pip install -r requirements.txt`
4. Set the start command to `gunicorn app:app`
5. Click "Create Web Service"

## Model Details

The linear regression model follows the equation:
```
package = 0.55795197 * cgpa - 0.8961119222429126
```

This means that for each additional point in CGPA, the predicted placement package increases by approximately 0.56 LPA.

## License

MIT 