import google.generativeai as genai
import os

# PASTE YOUR KEY HERE
API_KEY = "AIzaSyCI945GvitflUOjgHsyqpufFdI1ig6gWho"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print("Testing connection to Gemini 1.5 Flash...")
try:
    response = model.generate_content("Say 'System Online' if you can hear me.")
    print(f"SUCCESS! AI Replied: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")