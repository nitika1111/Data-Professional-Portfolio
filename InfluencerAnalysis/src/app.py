from flask import Flask, render_template, request
from googleapiclient.discovery import build
from google.cloud import language_v1
from textblob import TextBlob
from google.cloud import storage
import os
import json

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\DataScience-GCP\Projects\InfluencerAnalysis\src\sodium-replica-324907-4d7c9c4cf537.json"

# Set your YouTube API key
youtube_api_key = 'AIzaSyBAwxRPvS-LS2AkNM6J0imagMPT1f5MQjA'

# Set up storage client
storage_client = storage.Client()
bucket_name = 'influencer-analysis-bucket'

# Create language client
language_client = language_v1.LanguageServiceClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    channel_name = request.form['channel_name']

    # Call YouTube API to get channel information
    channel_info = get_channel_info(channel_name)

    print("Channel Info:", channel_info)
    if channel_info:
        # Get the latest video from the channel
        video_id = get_latest_video_id(channel_info['id'])
        print(">>>>>>>>>>>>>>>>>video_id:", video_id)

        # Get video details
        video_info = get_video_details(video_id)
        print(">>>>>>>>>>>>>>>>>video_info:", video_info)

        # Get video comments
        comments = get_video_comments(video_id)
        print(">>>>>>>>>>>>>>>>>comments:", comments)

        # Perform sentiment analysis
        sentiment_score = analyze_sentiment(comments)
        print(">>>>>>>>>>>>>>>>>sentiment_score:", sentiment_score)
    else:
        return render_template('error.html')

    return render_template('result.html', channel_info=channel_info, video_info=video_info,
                           video_id=video_id, sentiment_score=sentiment_score)

@app.route('/fetch_and_store_data', methods=['POST'])
def fetch_and_store_data():
    channel_name = request.form['channel_name']

    # Call YouTube API to get channel information
    channel_info = get_channel_info(channel_name)

    print("Channel Info:", channel_info)
    if channel_info:
        # Get the latest video from the channel
        video_id = get_latest_video_id(channel_info['id'])
        print(">>>>>>>>>>>>>>>>>video_id:", video_id)

        # Fetch YouTube raw data using the YouTube Data API
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        request = youtube.channels().list(part="snippet,contentDetails,statistics", id=channel_info['id'])
        response = request.execute()

        # Store the raw data in Cloud Storage
        blob = storage_client.bucket(bucket_name).blob(f"{channel_name}_raw_data.json")
        blob.upload_from_string(json.dumps(response))

        # Get video details
        video_info = get_video_details(video_id)
        print(">>>>>>>>>>>>>>>>>video_info:", video_info)

        # Get video comments
        comments = get_video_comments(video_id)
        print(">>>>>>>>>>>>>>>>>comments:", comments)

        # Perform sentiment analysis
        sentiment_score = analyze_sentiment(comments)
        print(">>>>>>>>>>>>>>>>>sentiment_score:", sentiment_score)
    else:
        return render_template('error.html')

    return render_template('result.html', channel_info=channel_info, video_info=video_info,
                           video_id=video_id, sentiment_score=sentiment_score)


def get_channel_info(channel_name):
    # Use YouTube API to get channel information
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    search_response = youtube.search().list(q=channel_name, type='channel', part='id').execute()

    if 'items' in search_response and search_response['items']:
        channel_id = search_response['items'][0]['id']['channelId']
        channel_response = youtube.channels().list(id=channel_id, part='snippet,contentDetails,statistics').execute()

        if 'items' in channel_response and channel_response['items']:
            channel_info = channel_response['items'][0]['snippet']
            channel_info['id'] = channel_id  # Add this line to include the channel ID
            channel_info['subscriberCount'] = channel_response['items'][0]['statistics']['subscriberCount']         
            return channel_info
    
    return None

def get_latest_video_id(channel_id):
    # Use YouTube API to get the latest video ID from the channel
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    videos_response = youtube.search().list(channelId=channel_id, type='video', part='id', order='date', maxResults=1).execute()

    if 'items' in videos_response and videos_response['items']:
        return videos_response['items'][0]['id']['videoId']

    return None

def get_video_details(video_id):
    # Use YouTube API to get details of a video
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    video_response = youtube.videos().list(id=video_id, part='snippet,statistics').execute()

    if 'items' in video_response and video_response['items']:
        print('\n',video_response['items'][0]['snippet'])
        return video_response['items'][0]['snippet']
    
    return None

def get_video_comments(video_id):
    # Use YouTube API to get comments from a video
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    comments_response = youtube.commentThreads().list(part='snippet', videoId=video_id, textFormat='plainText', maxResults=100).execute()

    if 'items' in comments_response:
        return [comment['snippet']['topLevelComment']['snippet']['textDisplay'] for comment in comments_response['items']]

    return []

def analyze_sentiment(comments):
    # Use Google Cloud Natural Language API for sentiment analysis
    document = language_v1.Document(content=' '.join(comments), type_=language_v1.Document.Type.PLAIN_TEXT)
    annotations = language_client.analyze_sentiment(request={'document': document})

    # Extract sentiment score
    sentiment_score = annotations.document_sentiment.score
    return sentiment_score

if __name__ == '__main__':
    app.run(debug=True)
