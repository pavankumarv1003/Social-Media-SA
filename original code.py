# Install necessary libraries
!pip install emoji vaderSentiment google-api-python-client asyncpraw matplotlib gradio

# Import required libraries
from googleapiclient.discovery import build
import re
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import asyncio
import asyncpraw

# Initialize YouTube API
YOUTUBE_API_KEY = 'AIzaSyAZVZl3zsxzxHuUopRE4IxK7324G9JlkiY'  
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Initialize Reddit API
async def reddit_client():
    return asyncpraw.Reddit(
        client_id="G0RYgpD26mS_rdPZ96cjrw",  
        client_secret="F3WDnmx2BRLSXNG5At85GHp__8XBBg",  
        user_agent="Python:UnifiedSentimentAnalyzer:v1.0 (by /u/yourusername)"
    )

# Sentiment analysis function
def sentiment_scores(comment):
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(comment)

# Analyze and display results
def analyze_and_display(comments):
    print("Analyzing sentiments...")
    polarity_scores = []
    positive_comments = []
    negative_comments = []
    neutral_comments = []

    for comment in comments:
        scores = sentiment_scores(comment)
        polarity_scores.append(scores['compound'])
        if scores['compound'] > 0.05:
            positive_comments.append(comment)
        elif scores['compound'] < -0.05:
            negative_comments.append(comment)
        else:
            neutral_comments.append(comment)

    print(f"Total Positive Comments: {len(positive_comments)}")
    print(f"Total Negative Comments: {len(negative_comments)}")
    print(f"Total Neutral Comments: {len(neutral_comments)}")

    avg_polarity = sum(polarity_scores) / len(polarity_scores)
    print(f"Average Polarity: {avg_polarity:.2f}")
    if avg_polarity > 0.05:
        print("Overall Sentiment: Positive")
    elif avg_polarity < -0.05:
        print("Overall Sentiment: Negative")
    else:
        print("Overall Sentiment: Neutral")

    # Visualization
    labels = ['Positive', 'Negative', 'Neutral']
    counts = [len(positive_comments), len(negative_comments), len(neutral_comments)]

    plt.bar(labels, counts, color=['blue', 'red', 'gray'])
    plt.title("Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Count")
    plt.show()

async def analyze_youtube():
    video_url = input('Enter YouTube Video URL: ')
    video_id = video_url[-11:]
    print("Video ID:", video_id)

    # Fetch comments
    print("Fetching Comments...")
    comments = []
    nextPageToken = None
    while len(comments) < 600:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            pageToken=nextPageToken
        )
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        nextPageToken = response.get('nextPageToken')
        if not nextPageToken:
            break

    print(f"Fetched {len(comments)} comments.")
    analyze_and_display(comments)

async def analyze_reddit():
    reddit = await reddit_client()
    post_url = input("Enter the Reddit post URL: ")

    submission = await reddit.submission(url=post_url)
    await submission.comments.replace_more(limit=None)

    comments = []
    count = 0
    for comment in submission.comments.list():
        comments.append(comment.body)
        count += 1
        if count >= 100:  # Limit comments to analyze
            break

    print(f"Fetched {len(comments)} comments.")
    analyze_and_display(comments)

async def main():
    print("Choose a platform for Sentiment Analysis:")
    print("1. YouTube")
    print("2. Reddit")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        await analyze_youtube()
    elif choice == '2':
        await analyze_reddit()
    else:
        print("Invalid choice. Exiting.")

await main()
