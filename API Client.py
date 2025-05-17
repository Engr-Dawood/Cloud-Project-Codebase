import requests
import json

# API Gateway URL
API_URL = "https://96hu0e1ele.execute-api.us-east-1.amazonaws.com/prod/generate"

# API key - replace with your actual API key
API_KEY = "YOUR_API_KEY_HERE"

# Request data
data = {
    "purpose": "Requesting information about a product",
    "recipient": "Sales department",
    "key_points": "Interested in pricing, availability, and technical specifications for Product X",
    "tone": "professional"
}

# Set headers including the API key
headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY  # This is the standard header for API Gateway API key authentication
}

# Make the request
try:
    response = requests.post(API_URL, headers=headers, json=data)
    
    # Print response status and content
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {str(e)}")
