from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
import os
import pandas as pd

app = Flask(__name__)

# Simple linear regression model
class SimpleLinearRegression:
    def __init__(self):
        self.slope = 0
        self.intercept = 0
        self.is_fitted = False
    
    def fit(self, X, y):
        X_mean = np.mean(X)
        y_mean = np.mean(y)
        
        # Calculate slope
        numerator = np.sum((X - X_mean) * (y - y_mean))
        denominator = np.sum((X - X_mean) ** 2)
        
        self.slope = numerator / denominator
        self.intercept = y_mean - (self.slope * X_mean)
        self.is_fitted = True
        return self
    
    def predict(self, X):
        if not self.is_fitted:
            raise Exception("Model not fitted yet")
        return self.slope * X + self.intercept

# Function to train the model
def train_model():
    try:
        # Sample data - CGPA vs Package
        data = {
            'cgpa': [6.89, 5.12, 7.82, 7.42, 6.94, 7.89, 6.73, 6.75, 6.19, 6.65],
            'package': [3.26, 1.98, 3.25, 3.67, 3.57, 3.78, 2.85, 3.74, 2.76, 2.87]
        }
        df = pd.DataFrame(data)
        
        X = df['cgpa'].values.reshape(-1, 1)
        y = df['package'].values
        
        model = SimpleLinearRegression()
        model.fit(X.flatten(), y)
        
        # Save the model parameters
        with open('model.pkl', 'wb') as f:
            pickle.dump(model, f)
        
        return model
    except Exception as e:
        print(f"Error in train_model: {str(e)}")
        return None

# Function to load or train the model
def load_or_train_model():
    try:
        if os.path.exists('model.pkl'):
            with open('model.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            return train_model()
    except Exception as e:
        print(f"Error in load_or_train_model: {str(e)}")
        return train_model()

# Load the model
model = load_or_train_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        cgpa = float(request.form['cgpa'])
        
        # Validate CGPA
        if cgpa < 0 or cgpa > 10:
            return jsonify({'error': 'CGPA must be between 0 and 10'})
        
        # Make prediction
        prediction = model.predict(np.array([cgpa]))[0]
        prediction = round(prediction, 2)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except ValueError:
        return jsonify({'error': 'Please enter a valid CGPA'})
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({'error': 'An error occurred during prediction'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)