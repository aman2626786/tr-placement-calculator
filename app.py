from flask import Flask, request, render_template, jsonify
import os
import json

# Create a more reliable way to find the templates and static files
app_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(app_dir, 'templates')
static_dir = os.path.join(app_dir, 'static')

# Initialize Flask with explicit template and static paths
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Counter file path
COUNTER_FILE = os.path.join(app_dir, 'user_counter.json')

# Function to get current user count
def get_user_count():
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
                return data.get('total_users', 0), data.get('predictions', 0)
        except:
            return 0, 0
    else:
        return 0, 0

# Function to increment user count
def increment_user_count(is_new_user=False):
    total_users, predictions = get_user_count()
    
    # Always increment predictions
    predictions += 1
    
    # Increment total_users only if it's a new user
    if is_new_user:
        total_users += 1
        
    # Save updated counts
    try:
        with open(COUNTER_FILE, 'w') as f:
            json.dump({
                'total_users': total_users,
                'predictions': predictions
            }, f)
    except Exception as e:
        print(f"Error saving counter: {str(e)}")
    
    return total_users, predictions

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

# Create model instance
model = load_model()

@app.route('/')
def home():
    # Get current user counts
    total_users, predictions = get_user_count()
    return render_template('index.html', total_users=total_users, predictions=predictions)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get CGPA from form
        cgpa = float(request.form.get('cgpa'))
        
        # Validate CGPA
        if cgpa < 0 or cgpa > 10:
            return render_template('index.html', error='CGPA must be between 0 and 10', cgpa=cgpa)
        
        # Make prediction
        prediction = model.predict(cgpa)
        
        # Round to 2 decimal places
        prediction = round(prediction, 2)
        
        # Format the prediction message
        prediction_message = f"With a CGPA of {cgpa}, your predicted package is ₹{prediction} LPA"
        
        # Increment the counter
        total_users, predictions = increment_user_count(is_new_user=request.cookies.get('user_visited') is None)
        
        # Render template with prediction
        response = render_template('index.html', 
                            prediction_text=prediction_message, 
                            cgpa=cgpa,
                            total_users=total_users,
                            predictions=predictions)
        
        # Set a cookie to track returning users
        resp = app.make_response(response)
        resp.set_cookie('user_visited', 'true', max_age=30*24*60*60)  # 30 days
        return resp
        
    except Exception as e:
        return render_template('index.html', error=f'Error: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True) 