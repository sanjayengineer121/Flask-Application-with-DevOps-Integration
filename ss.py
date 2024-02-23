import requests

# Set up authentication credentials
auth = ('username', 'password')

# Make a request to the login route to obtain the token
response = requests.get('http://localhost:5000/login', auth=auth)
token = response.json().get('token')

if token:
    # Set up headers with the obtained token
    headers = {'Authorization': f'Bearer {token}'}

    # Make a request to the homepage route with the headers
    response = requests.get('http://localhost:5000/', headers=headers)

    # Print the response
    print(response.text)
else:
    print("Failed to obtain token. Authentication failed.")
