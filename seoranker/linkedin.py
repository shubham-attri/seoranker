import requests
import json

def post_to_linkedin(access_token, person_id, message):
    url = 'https://api.linkedin.com/rest/posts'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    # Create the payload for the post
    payload = {
        "author": f"urn:li:person:{person_id}",
        "commentary": message,
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
        "lifecycleState": "PUBLISHED"
    }

    # Make the POST request to create a new post
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check if the request was successful
    if response.status_code == 201:
        print('Post created successfully:', response.json())
    else:
        print('Error creating post:', response.status_code, response.text)

if __name__ == "__main__":
    # Replace with your actual access token and LinkedIn person ID
    ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'  # Replace with your access token
    PERSON_ID = 'YOUR_PERSON_ID'          # Replace with your LinkedIn person ID
    MESSAGE = 'This is a test post from my Python script!'  # Your post message

    post_to_linkedin(ACCESS_TOKEN, PERSON_ID, MESSAGE)
