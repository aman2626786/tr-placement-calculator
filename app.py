from flask import Flask, request, render_template, jsonify, redirect
import os
import json
import sys
import shutil

# For debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir()}")

# Create Flask app with absolute path to template and static folders
app = Flask(__name__)

# Create directories if they don't exist
if not os.path.exists('templates'):
    os.makedirs('templates', exist_ok=True)
    print("Created templates directory")

if not os.path.exists('static'):
    os.makedirs('static', exist_ok=True)
    print("Created static directory")

# EMERGENCY FILE RELOCATION:
# Check if index.html is in the root directory but not in templates/
if os.path.exists('index.html') and not os.path.exists('templates/index.html'):
    try:
        print("Found index.html in root, copying to templates/")
        shutil.copy('index.html', 'templates/index.html')
        print("✅ Successfully copied index.html to templates/")
    except Exception as e:
        print(f"❌ Error copying index.html: {str(e)}")

# Check if style.css is in the root directory but not in static/
if os.path.exists('style.css') and not os.path.exists('static/style.css'):
    try:
        print("Found style.css in root, copying to static/")
        shutil.copy('style.css', 'static/style.css')
        print("✅ Successfully copied style.css to static/")
    except Exception as e:
        print(f"❌ Error copying style.css: {str(e)}")

# If templates directory exists at the current level, use it
if os.path.exists('templates'):
    app.template_folder = 'templates'
    print(f"Using templates folder: {os.path.abspath('templates')}")
    print(f"Templates directory contains: {os.listdir('templates')}")
# Also check if templates is in the /app directory (original structure)
elif os.path.exists('app/templates'):
    app.template_folder = 'app/templates'
    print(f"Using app/templates folder: {os.path.abspath('app/templates')}")
    print(f"Templates directory contains: {os.listdir('app/templates')}")
else:
    print("WARNING: Could not find templates directory!")
    # Try to create the directory and copy the template file if needed
    if not os.path.exists('templates'):
        os.makedirs('templates', exist_ok=True)
        print("Created templates directory")

# Same for static files
if os.path.exists('static'):
    app.static_folder = 'static'
    print(f"Using static folder: {os.path.abspath('static')}")
# Also check if static is in the /app directory (original structure)
elif os.path.exists('app/static'):
    app.static_folder = 'app/static'
    print(f"Using app/static folder: {os.path.abspath('app/static')}")
else:
    print("WARNING: Could not find static directory!")
    # Try to create the directory if needed
    if not os.path.exists('static'):
        os.makedirs('static', exist_ok=True)
        print("Created static directory")

# Counter file path - use the same directory as the app.py file
COUNTER_FILE = os.path.join(os.getcwd(), 'user_counter.json')
print(f"Using counter file: {COUNTER_FILE}")

# Function to get current user count
def get_user_count():
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
                return data.get('total_users', 0), data.get('predictions', 0)
        except Exception as e:
            print(f"Error reading counter file: {str(e)}")
            return 0, 0
    else:
        print(f"Counter file does not exist: {COUNTER_FILE}")
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
    try:
        return render_template('index.html', total_users=total_users, predictions=predictions)
    except Exception as e:
        error_message = f"Error rendering template: {str(e)}<br>App template folder: {app.template_folder}<br>Current directory: {os.getcwd()}"
        print(error_message)
        
        # Emergency fallback - check if we need to create a template 
        if not os.path.exists('templates/index.html'):
            return redirect('/emergency-create-template', code=307)
        
        return error_message

@app.route('/debug')
def debug():
    # This route provides detailed debugging information
    info = {
        'Current Working Directory': os.getcwd(),
        'Python Version': sys.version,
        'Template Folder': app.template_folder,
        'Static Folder': app.static_folder,
        'Environment': os.environ.get('FLASK_ENV', 'Not set'),
        'Files in Current Directory': os.listdir(),
        'Files in templates (if exists)': os.listdir('templates') if os.path.exists('templates') else 'Directory not found',
        'Files in static (if exists)': os.listdir('static') if os.path.exists('static') else 'Directory not found',
        'Files in app/templates (if exists)': os.listdir('app/templates') if os.path.exists('app/templates') else 'Directory not found',
        'Files in app/static (if exists)': os.listdir('app/static') if os.path.exists('app/static') else 'Directory not found',
    }
    
    # Check index.html existence
    if os.path.exists('templates/index.html'):
        info['index.html in templates'] = 'Exists'
        try:
            with open('templates/index.html', 'r') as f:
                info['index.html size'] = len(f.read())
        except Exception as e:
            info['index.html read error'] = str(e)
    else:
        info['index.html in templates'] = 'NOT FOUND'
    
    # Return as HTML
    html = "<h1>Debug Information</h1>"
    html += "<table border='1'>"
    for key, value in info.items():
        html += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
    html += "</table>"
    
    # Add emergency content creation button
    html += """
    <h2>Emergency Actions</h2>
    <form action="/emergency-create-template" method="post">
        <button type="submit">Create Emergency Template</button>
    </form>
    """
    
    return html

@app.route('/emergency-create-template', methods=['GET', 'POST'])
def emergency_create_template():
    # This route creates a minimal emergency template
    try:
        os.makedirs('templates', exist_ok=True)
        print("Created templates directory for emergency template")
        
        # First check if index.html exists in the root directory
        if os.path.exists('index.html'):
            try:
                print("Found index.html in root, copying to templates/")
                shutil.copy('index.html', 'templates/index.html')
                print("Successfully copied index.html to templates/")
                # Reset the Flask template path
                app.template_folder = 'templates'
                return "Found and copied index.html to templates directory! <a href='/'>Go to homepage</a>"
            except Exception as e:
                print(f"Error copying index.html: {str(e)}")
        
        # Create a minimal index.html file
        minimal_template = """<!DOCTYPE html>
<html>
<head>
    <title>TR Placement Predictor - Emergency Mode</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .footer { margin-top: 40px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>TR Placement Predictor</h1>
        <p>Emergency Mode</p>
        
        <div class="card">
            <h2>CGPA to Package Calculator</h2>
            <form action="/predict" method="post">
                <div>
                    <label for="cgpa">Enter your CGPA (0-10):</label>
                    <input type="number" id="cgpa" name="cgpa" step="0.01" min="0" max="10" required>
                </div>
                <div style="margin-top: 20px;">
                    <button type="submit" class="btn">Predict Package</button>
                </div>
            </form>
        </div>
        
        <div class="footer">
            <p>© 2023 TR Placement Predictor | Designed & Developed by Aman Sharma</p>
        </div>
    </div>
</body>
</html>"""
        
        with open('templates/index.html', 'w') as f:
            f.write(minimal_template)
        
        # Reset the Flask template path
        app.template_folder = 'templates'
        
        return "Emergency template created successfully! <a href='/'>Go to homepage</a>"
    except Exception as e:
        return f"Error creating emergency template: {str(e)}"

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