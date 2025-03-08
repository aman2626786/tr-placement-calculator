import os
import sys
import unittest
from app import app, load_model

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page(self):
        """Test that home page loads properly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TR', response.data)  # Check for logo
        self.assertIn(b'Placement Predictor', response.data)
    
    def test_prediction(self):
        """Test prediction functionality with valid CGPA"""
        response = self.app.post('/predict', data=dict(cgpa='8.5'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'predicted package', response.data)
    
    def test_invalid_input(self):
        """Test error handling with invalid CGPA"""
        response = self.app.post('/predict', data=dict(cgpa='15'))  # Invalid CGPA
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'must be between 0 and 10', response.data)
    
    def test_model_prediction(self):
        """Test the model itself"""
        model = load_model()
        prediction = model.predict(8.5)
        self.assertIsInstance(prediction, float)
        self.assertGreater(prediction, 0)  # Prediction should be positive

if __name__ == '__main__':
    unittest.main() 