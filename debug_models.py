import google.generativeai as genai
import os

# PASTE YOUR KEY HERE
API_KEY = "AIzaSyCI945GvitflUOjgHsyqpufFdI1ig6gWho"

genai.configure(api_key=API_KEY)

print("Scanning for available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"AVAILABLE: {m.name}")
except Exception as e:
    print(f"ERROR: {e}")