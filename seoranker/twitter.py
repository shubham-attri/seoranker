import requests
from requests_oauthlib import OAuth1

# Replace these values with your own keys and tokens
API_KEY = 'YOUR_API_KEY'
API_SECRET_KEY = 'YOUR_API_SECRET_KEY'
ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'YOUR_ACCESS_TOKEN_SECRET'

# Function to post a tweet
def post_tweet(tweet_text, in_reply_to_status_id=None):
    url = "https://api.twitter.com/2/tweets"
    
    # Set up OAuth1 authentication
    auth = OAuth1(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Create the payload for the tweet
    payload = {"text": tweet_text}
    if in_reply_to_status_id:
        payload["in_reply_to_status_id"] = in_reply_to_status_id

    # Make the POST request to create a new tweet
    response = requests.post(url, auth=auth, json=payload)

    # Check if the request was successful
    if response.status_code == 201:
        print("Tweet posted successfully:", response.json())
        return response.json()['data']['id']  # Return the ID of the posted tweet
    else:
        print("Error posting tweet:", response.status_code, response.text)
        return None

# Function to create a thread of tweets
def create_thread(tweet_texts):
    last_tweet_id = None
    for text in tweet_texts:
        last_tweet_id = post_tweet(text, last_tweet_id)

if __name__ == "__main__":
    # List of tweets for the thread
    tweets = [
        "This is the first tweet in my thread.",
        "This is the second tweet, replying to the first.",
        "And this is the third tweet, continuing the thread."
    ]
    
    create_thread(tweets)
