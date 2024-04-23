import requests

response = requests.post('http://scribe_app:8000/healthcheck/internal', data={'host_key': 'bruh'})
print(response.text)  # Print the response text