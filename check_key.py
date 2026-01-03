import google.generativeai as genai
import os

key = 'AIzaSyAkch32yvh3tKb0NZlDPUTCdyiHfsTOrko'
genai.configure(api_key=key)

model = genai.GenerativeModel('gemini-flash-latest')
try:
    response = model.generate_content("Hello")
    print("SUCCESS: " + response.text)
except Exception as e:
    print("FAIL: " + str(e))
