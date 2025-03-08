from flask import Flask, request, render_template, jsonify

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Load the model
def load_model():
    # Model coefficients from the notebook
    # y = mx + b
    m = 0.55795197
    b = -0.8961119222429126
    
    # Simple model class to make predictions
    class SimpleLinearModel:
        def __init__(self, m, b):
            self.m = m
            self.b = b
        
        def predict(self, X):
            return self.m * X + self.b
    
    return SimpleLinearModel(m, b)

# Load model
model = load_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the CGPA from the form
        cgpa = float(request.form['cgpa'])
        
        # Validate CGPA input
        if cgpa < 0 or cgpa > 10:
            return render_template('index.html', error='CGPA must be between 0 and 10')
        
        # Make prediction
        placement_package = model.predict(cgpa)
        
        # Round to 2 decimal places for better display
        placement_package = round(float(placement_package), 2)
        
        # Create a nice message with the prediction
        prediction_message = f'Predicted Package: ₹{placement_package} LPA'
        
        return render_template('index.html', 
                              prediction_text=prediction_message,
                              cgpa=cgpa)
    except Exception as e:
        return render_template('index.html', 
                              error=f'Error in prediction: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True) 