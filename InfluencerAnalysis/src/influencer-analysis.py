import os
from googleapiclient.discovery import build
from google.cloud import language_v1
from google.cloud.language_v1 import types

# Set your YouTube API key
# Replace 'YOUR_YOUTUBE_API_KEY' with the actual API key you obtained
youtube_api_key = 'AIzaSyBAwxRPvS-LS2AkNM6J0imagMPT1f5MQjA'

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

service_account_key_path = 'D:\DataScience-GCP\Projects\InfluencerAnalysis\src\sodium-replica-324907-1de8404a91e9.json'


def get_channel_info(channel_name):
    # Search for the channel ID based on the channel name
    search_response = youtube.search().list(
        q=channel_name,
        type='channel',
        part='id',
        maxResults=1
    ).execute()

    # Extract the channel ID from the search results
    if 'items' in search_response and search_response['items']:
        channel_id = search_response['items'][0]['id']['channelId']
    else:
        print("Channel not found.")
        return None

    # Get information about the channel
    channel_response = youtube.channels().list(
        id=channel_id,
        part='snippet,contentDetails,statistics'
    ).execute()

    # Extract relevant information from the channel response
    if 'items' in channel_response and channel_response['items']:
        channel_info = channel_response['items'][0]
        return channel_info
    else:
        print("Error retrieving channel information.")
        return None

def analyze_sentiment(comments):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key_path
    client = language_v1.LanguageServiceClient()

    document = language_v1.Document(
        content=' '.join(comments),
        type_=types.Document.Type.PLAIN_TEXT
    )

    sentiment = client.analyze_sentiment(document=document).document_sentiment
    return sentiment.score

# Example usage:
channel_name_input = input("Enter the channel name: ")
channel_info = get_channel_info(channel_name_input)
language_api_key = 'AIzaSyCc4MYWU9c6miGPQE9YLqgfhDpKjxESkgw'  # Replace with your Natural Language API key

if channel_info:
    print("Channel Name:", channel_info['snippet']['title'])
    print("Channel ID:", channel_info['id'])
    print("Subscriber Count:", channel_info['statistics']['subscriberCount'])
    
    # Get the latest videos from the channel
    videos_response = youtube.search().list(
        channelId=channel_info['id'],
        type='video',
        part='id',
        order='date',
        maxResults=5  # You can adjust this value based on your needs
    ).execute()

    video_ids = [video['id']['videoId'] for video in videos_response.get('items', [])]

    # Perform sentiment analysis on comments of the latest videos
    for video_id in video_ids:
        comments_response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100  # You can adjust this value based on your needs
        ).execute()

        # Extract comments from the response
        comments = [comment['snippet']['topLevelComment']['snippet']['textDisplay']
                    for comment in comments_response.get('items', [])]

        # Perform sentiment analysis using the Natural Language API
        sentiment_score = analyze_sentiment(comments)

        print(f"\nVideo ID: {video_id}")
        print(f"Average Sentiment Score: {sentiment_score}")
else:
    print("Channel information not available.")
