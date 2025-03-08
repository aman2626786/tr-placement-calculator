from flask import Flask, render_template, request, jsonify
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import joblib
import os

app = Flask(__name__)

# Load and train the model
def train_model():
    # Read the dataset from the provided path
    data = pd.read_csv('placement_data.csv')
    X = data[['cgpa']]
    y = data['package']
    
    # Create and train the model
    model = LinearRegression()
    model.fit(X, y)
    
    # Save the model
    joblib.dump(model, 'model.pkl')
    return model

def load_or_train_model():
    if os.path.exists('model.pkl'):
        return joblib.load('model.pkl')
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
        prediction = model.predict([[cgpa]])[0]
        prediction = round(prediction, 2)  # Round to 2 decimal places
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except ValueError:
        return jsonify({'error': 'Please enter a valid CGPA'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 