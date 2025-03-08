# Placement Salary Predictor

A web application that predicts placement salary (in LPA - Lakhs Per Annum) based on CGPA using Machine Learning. The application uses Linear Regression to make predictions based on historical placement data.

## Features

- Simple and intuitive user interface
- Real-time predictions
- Input validation for CGPA
- Responsive design that works on both desktop and mobile
- RESTful API endpoint for predictions

## Prerequisites

Before running this application, make sure you have the following installed:
- Python 3.7 or higher
- pip (Python package manager)

## Installation Steps

1. Clone or download this repository to your local machine

2. Open a terminal/command prompt and navigate to the project directory:
   ```bash
   cd path/to/placement-predictor
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure you have the placement dataset (`placement_data.csv`) in the project root directory
   - The CSV file should have two columns: 'cgpa' and 'package'
   - If you don't have the file, copy it from: `C:\Users\aman2\Downloads\placement (1).csv`

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

3. You should see the prediction interface where you can:
   - Enter a CGPA value between 0 and 10
   - Click "Predict Placement Salary"
   - View the predicted salary in LPA

## Project Structure

```
placement-predictor/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── placement_data.csv  # Dataset for training
├── model.pkl          # Trained model (generated automatically)
└── templates/
    └── index.html     # Frontend interface
```

## API Usage

The application provides a REST API endpoint for predictions:

- **Endpoint**: `/predict`
- **Method**: POST
- **Parameters**: 
  - `cgpa`: float (between 0 and 10)
- **Response Format**:
  ```json
  {
    "success": true,
    "prediction": 3.45  // Predicted salary in LPA
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "Error message here"
  }
  ```

## Technologies Used

- Backend:
  - Flask (Python web framework)
  - scikit-learn (Machine Learning library)
  - pandas (Data manipulation)
  - numpy (Numerical computations)

- Frontend:
  - HTML5
  - CSS3
  - Bootstrap 5
  - jQuery
  - AJAX

## Troubleshooting

1. If you see "Model not found" error:
   - Ensure `placement_data.csv` is in the project directory
   - Restart the application

2. If the application doesn't start:
   - Check if port 5000 is available
   - Ensure all dependencies are installed correctly

## Support

For any issues or questions, please:
1. Check the troubleshooting section
2. Verify your Python version and dependencies
3. Ensure the dataset is properly formatted

## License

This project is open source and available for educational and personal use. 