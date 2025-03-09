from flask import Flask, request, render_template, jsonify, redirect
import os
import sys
import secrets
import json
from datetime import datetime
import uuid  # For generating unique IDs

# For debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir()}")

# Create Flask app
app = Flask(__name__)

# In-memory fallback stats (used if database connection fails)
in_memory_stats = {"total_users": 10, "predictions": 25}

# Initialize database connection
try:
    # Check if pymongo is installed
    import pymongo
    
    # MongoDB connection (we'll use environment variable in production)
    MONGO_URI = os.environ.get("MONGO_URI")
    
    if MONGO_URI:
        # Connect to MongoDB if URI is provided
        client = pymongo.MongoClient(MONGO_URI)
        db = client["placement_predictor"]
        stats_collection = db["stats"]
        predictions_collection = db["predictions"]
        visitors_collection = db["visitors"]  # Added collection for visitor data
        feedback_collection = db["feedback"]  # Added collection for feedback
        
        # Create or update the stats document
        stats = stats_collection.find_one({"_id": "counter"})
        if not stats:
            stats_collection.insert_one({
                "_id": "counter",
                "total_users": 0,
                "predictions": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
        print("✅ MongoDB connection successful")
        using_mongodb = True
    else:
        print("⚠️ No MongoDB URI provided, using fallback storage")
        using_mongodb = False
except ImportError:
    print("⚠️ pymongo not installed, using fallback storage")
    using_mongodb = False
except Exception as e:
    print(f"❌ MongoDB connection error: {str(e)}")
    using_mongodb = False

# Counter file path - use the same directory as the app.py file (fallback method)
COUNTER_FILE = os.path.join(os.getcwd(), 'user_counter.json')

# Check for templates and static directories and create if missing
if not os.path.exists('templates'):
    os.makedirs('templates', exist_ok=True)
    print("Created templates directory")

if not os.path.exists('static'):
    os.makedirs('static', exist_ok=True)
    print("Created static directory")

# Check if index.html and style.css are in root and copy to respective directories
if os.path.exists('index.html') and not os.path.exists('templates/index.html'):
    try:
        with open('index.html', 'r') as src, open('templates/index.html', 'w') as dst:
            dst.write(src.read())
        print("✅ Successfully copied index.html to templates/")
    except Exception as e:
        print(f"❌ Error copying index.html: {str(e)}")

if os.path.exists('style.css') and not os.path.exists('static/style.css'):
    try:
        with open('style.css', 'r') as src, open('static/style.css', 'w') as dst:
            dst.write(src.read())
        print("✅ Successfully copied style.css to static/")
    except Exception as e:
        print(f"❌ Error copying style.css: {str(e)}")

# Set template and static folders
if os.path.exists('templates'):
    app.template_folder = 'templates'
    print(f"Using templates folder: {os.path.abspath('templates')}")
    print(f"Templates directory contains: {os.listdir('templates')}")
else:
    print("WARNING: Could not find templates directory!")

if os.path.exists('static'):
    app.static_folder = 'static'
    print(f"Using static folder: {os.path.abspath('static')}")
else:
    print("WARNING: Could not find static directory!")

# Track visitor data
def track_visitor(user_id, ip_address=None, user_agent=None, path=None):
    if using_mongodb:
        try:
            visitors_collection.insert_one({
                "user_id": user_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "path": path,
                "timestamp": datetime.now()
            })
            print(f"✅ Visitor tracked: {user_id}")
        except Exception as e:
            print(f"❌ Error tracking visitor: {str(e)}")

# Function to get current user count
def get_user_count():
    if using_mongodb:
        try:
            stats = stats_collection.find_one({"_id": "counter"})
            if stats:
                return stats.get("total_users", 0), stats.get("predictions", 0)
            return 0, 0
        except Exception as e:
            print(f"Error reading from MongoDB: {str(e)}")
            # Fallback to file if MongoDB fails
            pass
    
    # Fallback to file-based storage if MongoDB is not available
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
                return data.get('total_users', 0), data.get('predictions', 0)
        else:
            # If counter file doesn't exist, use in-memory fallback
            return in_memory_stats.get("total_users", 0), in_memory_stats.get("predictions", 0)
    except Exception as e:
        print(f"Error reading counter file: {str(e)}")
        return in_memory_stats.get("total_users", 0), in_memory_stats.get("predictions", 0)

# Function to increment user count
def increment_user_count(is_new_user=False):
    if using_mongodb:
        try:
            update_data = {"$inc": {"predictions": 1}, "$set": {"updated_at": datetime.now()}}
            
            if is_new_user:
                update_data["$inc"]["total_users"] = 1
            
            result = stats_collection.update_one(
                {"_id": "counter"},
                update_data
            )
            
            # Get and return the updated counts
            stats = stats_collection.find_one({"_id": "counter"})
            if stats:
                return stats.get("total_users", 0), stats.get("predictions", 0)
            return 0, 0
        except Exception as e:
            print(f"Error updating MongoDB: {str(e)}")
            # Fallback to file if MongoDB fails
            pass
    
    # Fallback to file-based storage
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
        # Update in-memory stats as last resort
        in_memory_stats["predictions"] += 1
        if is_new_user:
            in_memory_stats["total_users"] += 1
        total_users, predictions = in_memory_stats.get("total_users", 0), in_memory_stats.get("predictions", 0)
    
    return total_users, predictions

# Function to log a prediction
def log_prediction(cgpa, prediction, user_id):
    if using_mongodb:
        try:
            predictions_collection.insert_one({
                "cgpa": cgpa,
                "prediction": prediction,
                "user_id": user_id,
                "timestamp": datetime.now()
            })
            print(f"✅ Prediction logged: CGPA {cgpa}, Package {prediction}")
        except Exception as e:
            print(f"❌ Error logging prediction: {str(e)}")

# Function to save feedback
def save_feedback(user_id, name, email, message, rating):
    if using_mongodb:
        try:
            feedback_collection.insert_one({
                "user_id": user_id,
                "name": name,
                "email": email,
                "message": message,
                "rating": rating,
                "timestamp": datetime.now()
            })
            return True
        except Exception as e:
            print(f"❌ Error saving feedback to MongoDB: {str(e)}")
            # If MongoDB fails, fall back to file storage
            pass
    
    # Fallback to JSON file storage if MongoDB is not available or fails
    try:
        feedback_data = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "message": message,
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        }
        
        # Path for feedback file
        feedback_file = os.path.join(os.getcwd(), 'feedback.json')
        
        # Check if file exists and load existing data
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r') as f:
                    all_feedback = json.load(f)
            except:
                all_feedback = []
        else:
            all_feedback = []
        
        # Add new feedback and save
        all_feedback.append(feedback_data)
        with open(feedback_file, 'w') as f:
            json.dump(all_feedback, f, indent=2)
        
        print(f"✅ Feedback saved to file: {feedback_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving feedback to file: {str(e)}")
        return False

# Load the model
def load_model():
    # Model coefficients
    m = 0.55795197
    b = -0.8961119222429126
    
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
    # Get or create user_id from cookie
    user_id = request.cookies.get('user_id')
    is_new_user = user_id is None
    
    if is_new_user:
        user_id = secrets.token_hex(16)
        
    # Track visitor
    track_visitor(
        user_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        path='/'
    )
    
    # Get current user counts
    total_users, predictions = get_user_count()
    
    try:
        response = render_template('index.html', 
                              total_users=total_users, 
                              predictions=predictions)
        
        # Set cookie if new user
        if is_new_user:
            resp = app.make_response(response)
            resp.set_cookie('user_id', user_id, max_age=365*24*60*60)  # 1 year
            return resp
            
        return response
        
    except Exception as e:
        error_message = f"Error rendering template: {str(e)}<br>App template folder: {app.template_folder}<br>Current directory: {os.getcwd()}"
        print(error_message)
        
        # Emergency fallback - check if we need to create a template 
        if not os.path.exists('templates/index.html'):
            return redirect('/emergency-create-template', code=307)
        
        return error_message

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        user_id = request.cookies.get('user_id', secrets.token_hex(16))
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        message = request.form.get('message', '')
        rating = request.form.get('rating', 5)
        
        # Convert rating to integer
        try:
            rating = int(rating)
        except:
            rating = 5
            
        # Save feedback
        success = save_feedback(user_id, name, email, message, rating)
        
        # Get current counts for rendering the page
        total_users, predictions = get_user_count()
        
        # Return thank you page or message
        if success:
            return render_template('index.html', 
                             feedback_success=True, 
                             total_users=total_users, 
                             predictions=predictions)
        else:
            return render_template('index.html', 
                             feedback_error="Unable to save feedback. Please try again later.", 
                             total_users=total_users, 
                             predictions=predictions)
            
    except Exception as e:
        return render_template('index.html', 
                         feedback_error=f"Error: {str(e)}", 
                         total_users=get_user_count()[0], 
                         predictions=get_user_count()[1])

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
        'Using MongoDB': using_mongodb
    }
    
    # Check MongoDB connection
    if using_mongodb:
        try:
            client.admin.command('ping')
            info['MongoDB Ping'] = "Success"
            
            # Get stats
            stats = stats_collection.find_one({"_id": "counter"})
            if stats:
                info['MongoDB Stats'] = str(stats)
            else:
                info['MongoDB Stats'] = "No stats found"
                
            # Get recent predictions (last 5)
            recent_predictions = list(predictions_collection.find().sort("timestamp", -1).limit(5))
            if recent_predictions:
                info['Recent Predictions'] = str(recent_predictions)
            else:
                info['Recent Predictions'] = "No predictions found"
                
            # Get recent visitors (last 5)
            recent_visitors = list(visitors_collection.find().sort("timestamp", -1).limit(5))
            if recent_visitors:
                info['Recent Visitors'] = str(recent_visitors)
            else:
                info['Recent Visitors'] = "No visitors found"
                
            # Get recent feedback (last 5)
            recent_feedback = list(feedback_collection.find().sort("timestamp", -1).limit(5))
            if recent_feedback:
                info['Recent Feedback'] = str(recent_feedback)
            else:
                info['Recent Feedback'] = "No feedback found"
                
        except Exception as e:
            info['MongoDB Error'] = str(e)
    
    # Check counter file
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
                info['Counter File Content'] = str(data)
        except Exception as e:
            info['Counter File Error'] = str(e)
    else:
        info['Counter File'] = "Does not exist"
        
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
        html += f"<tr><td><b>{key}</b></td><td>{str(value)}</td></tr>"
    html += "</table>"
    
    # Add emergency content creation button
    html += """
    <h2>Emergency Actions</h2>
    <form action="/emergency-create-template" method="post">
        <button type="submit">Create Emergency Template</button>
    </form>
    """
    
    if using_mongodb:
        html += """
        <form action="/reset-database" method="post">
            <button type="submit">Reset Counter Database</button>
        </form>
        """
    else:
        html += """
        <form action="/reset-counter-file" method="post">
            <button type="submit">Reset Counter File</button>
        </form>
        """
    
    return html

@app.route('/reset-database', methods=['POST'])
def reset_database():
    if using_mongodb:
        try:
            stats_collection.update_one(
                {"_id": "counter"},
                {"$set": {"total_users": 0, "predictions": 0, "updated_at": datetime.now()}}
            )
            return "Database counters reset successfully! <a href='/debug'>Back to Debug</a>"
        except Exception as e:
            return f"Error resetting database: {str(e)}"
    else:
        return "MongoDB not available. <a href='/debug'>Back to Debug</a>"

@app.route('/reset-counter-file', methods=['POST'])
def reset_counter_file():
    try:
        with open(COUNTER_FILE, 'w') as f:
            json.dump({
                'total_users': 0,
                'predictions': 0
            }, f)
        return "Counter file reset successfully! <a href='/debug'>Back to Debug</a>"
    except Exception as e:
        return f"Error resetting counter file: {str(e)}"

@app.route('/emergency-create-template', methods=['GET', 'POST'])
def emergency_create_template():
    # This route creates a minimal emergency template
    try:
        os.makedirs('templates', exist_ok=True)
        print("Created templates directory for emergency template")
        
        # First check if index.html exists in the root directory
        if os.path.exists('index.html'):
            try:
                with open('index.html', 'r') as src, open('templates/index.html', 'w') as dst:
                    dst.write(src.read())
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
        body { font-family: Arial; margin: 40px; background-color: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; }
        .logo-container { display: flex; justify-content: center; margin-bottom: 20px; }
        .logo { width: 70px; height: 70px; background: linear-gradient(45deg, #0062E6, #33AEFF); 
                border-radius: 12px; display: flex; align-items: center; justify-content: center; 
                color: white; font-weight: bold; font-size: 28px; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; 
               background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .btn { background: linear-gradient(135deg, #0062E6, #33AEFF); color: white; 
              border: none; padding: 10px 20px; border-radius: 30px; cursor: pointer; 
              font-weight: bold; transition: all 0.3s ease; }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 6px 8px rgba(0, 123, 255, 0.4); }
        .footer { margin-top: 40px; text-align: center; color: #6c757d; }
        .user-counter-container { display: flex; justify-content: center; margin: 20px auto; 
                                 background: rgba(255,255,255,0.9); padding: 15px 30px; 
                                 border-radius: 50px; max-width: 450px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .counter-item { text-align: center; padding: 0 20px; }
        .counter-value { font-size: 28px; font-weight: 700; color: #0062E6; margin-bottom: 5px; }
        .counter-label { font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: #6c757d; }
        .counter-divider { width: 1px; height: 40px; background: rgba(0, 123, 255, 0.3); }
        h1, h2 { text-align: center; }
        .feedback-form { margin-top: 30px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .rating { display: flex; justify-content: center; margin: 15px 0; }
        .rating input { display: none; }
        .rating label { cursor: pointer; font-size: 30px; color: #ddd; }
        .rating label:hover, .rating label:hover ~ label, .rating input:checked ~ label { color: #ffcc00; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-container">
            <div class="logo">TR</div>
        </div>
        <h1>Placement Predictor</h1>
        
        <div class="user-counter-container">
            <div class="counter-item">
                <div class="counter-value">{{ total_users|default(0) }}</div>
                <div class="counter-label">Total Users</div>
            </div>
            <div class="counter-divider"></div>
            <div class="counter-item">
                <div class="counter-value">{{ predictions|default(0) }}</div>
                <div class="counter-label">Predictions Made</div>
            </div>
        </div>
        
        <div class="card">
            <h2>CGPA to Package Calculator</h2>
            <form action="/predict" method="post">
                <div style="margin-bottom: 20px;">
                    <label for="cgpa">Enter your CGPA (0-10):</label>
                    <input type="number" id="cgpa" name="cgpa" step="0.01" min="0" max="10" required
                           style="width: 100%; padding: 10px; margin-top: 5px; border-radius: 5px; border: 1px solid #ced4da;">
                </div>
                
                {% if prediction_text %}
                <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
                    <h4>{{ prediction_text }}</h4>
                    <p>Congratulations on your achievement!</p>
                </div>
                {% endif %}
                
                {% if error %}
                <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
                    <h5>{{ error }}</h5>
                </div>
                {% endif %}
                
                <div style="text-align: center; margin-top: 20px;">
                    <button type="submit" class="btn">Predict Package</button>
                </div>
            </form>
        </div>
        
        <div class="card">
            <h3 style="text-align: center;">About This Predictor</h3>
            <p>This application uses a <strong>Linear Regression</strong> model trained on placement data to predict your package based on CGPA.</p>
        </div>
        
        <!-- Feedback Form -->
        <div class="card feedback-form">
            <h3 style="text-align: center;">Feedback</h3>
            
            {% if feedback_success %}
            <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
                <h5>Thank you for your feedback!</h5>
            </div>
            {% endif %}
            
            {% if feedback_error %}
            <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
                <h5>{{ feedback_error }}</h5>
            </div>
            {% endif %}
            
            <form action="/feedback" method="post">
                <div class="form-group">
                    <label for="name">Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="message">Message</label>
                    <textarea id="message" name="message" rows="4" required></textarea>
                </div>
                <div class="form-group">
                    <label>Rating</label>
                    <div class="rating">
                        <input type="radio" id="star5" name="rating" value="5" checked>
                        <label for="star5">★</label>
                        <input type="radio" id="star4" name="rating" value="4">
                        <label for="star4">★</label>
                        <input type="radio" id="star3" name="rating" value="3">
                        <label for="star3">★</label>
                        <input type="radio" id="star2" name="rating" value="2">
                        <label for="star2">★</label>
                        <input type="radio" id="star1" name="rating" value="1">
                        <label for="star1">★</label>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <button type="submit" class="btn">Submit Feedback</button>
                </div>
            </form>
        </div>
        
        <div class="footer">
            <p>© 2023 TR Placement Predictor | Created for academic purposes</p>
            <p style="font-size: 12px; color: #6c757d;">Designed & Developed by Aman Sharma</p>
        </div>
    </div>
    
    <script>
        // Simple animation for counters
        document.addEventListener('DOMContentLoaded', function() {
            const counterValues = document.querySelectorAll('.counter-value');
            counterValues.forEach(value => {
                const finalValue = parseInt(value.textContent);
                let startValue = 0;
                const duration = 1500;
                const increment = finalValue / (duration / 16);
                
                const timer = setInterval(() => {
                    startValue += increment;
                    value.textContent = Math.floor(startValue);
                    
                    if(startValue >= finalValue) {
                        value.textContent = finalValue;
                        clearInterval(timer);
                    }
                }, 16);
            });
            
            // Star rating functionality
            const stars = document.querySelectorAll('.rating label');
            stars.forEach((star, index) => {
                star.addEventListener('click', () => {
                    document.getElementById('star' + (5-index)).checked = true;
                });
            });
        });
    </script>
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
        
        # Get or create user_id from cookie
        user_id = request.cookies.get('user_id')
        is_new_user = user_id is None
        
        if is_new_user:
            user_id = secrets.token_hex(16)
        
        # Track visitor
        track_visitor(
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            path='/predict'
        )
        
        # Log this prediction
        if using_mongodb:
            log_prediction(cgpa, prediction, user_id)
        
        # Increment the counter
        total_users, predictions = increment_user_count(is_new_user=is_new_user)
        
        # Render template with prediction
        response = render_template('index.html', 
                           prediction_text=prediction_message, 
                           cgpa=cgpa,
                           total_users=total_users,
                           predictions=predictions)
        
        # Create response object to set cookie
        resp = app.make_response(response)
        
        # Set a cookie to track returning users if it's a new user
        if is_new_user:
            resp.set_cookie('user_id', user_id, max_age=365*24*60*60)  # 1 year expiry
        
        return resp
        
    except Exception as e:
        return render_template('index.html', error=f'Error: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True) 