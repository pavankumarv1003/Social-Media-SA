!pip install gradio

# Install necessary libraries
!pip install gradio matplotlib emoji vaderSentiment google-api-python-client asyncpraw

# Import libraries
import gradio as gr
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
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
        user_agent="Python:UnifiedSentimentAnalyzer:v1.0 (by /u/ig_Mr_Ted)"
    )

# Sentiment analysis function
def sentiment_scores(comment):
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(comment)

# Function to analyze comments and return graph and concise description
def analyze_comments(comments, platform):
    positive, negative, neutral = 0, 0, 0

    for comment in comments:
        scores = sentiment_scores(comment)
        if scores['compound'] > 0.05:
            positive += 1
        elif scores['compound'] < -0.05:
            negative += 1
        else:
            neutral += 1

    # Generate sentiment distribution graph
    labels = ['Positive', 'Negative', 'Neutral']
    counts = [positive, negative, neutral]

    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['blue', 'red', 'gray'])
    plt.title(f"Sentiment Distribution ({platform})", fontsize=14)
    plt.xlabel("Sentiment", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    graph_path = "sentiment_distribution.png"
    plt.savefig(graph_path)
    plt.close()

    # Generate concise description
    total_comments = len(comments)
    overall_sentiment = (
        "Positive" if positive > negative else
        "Negative" if negative > positive else
        "Neutral"
    )
    description = (
        f"Out of {total_comments} comments analyzed, "
        f"{positive} are Positive, {negative} are Negative, and {neutral} are Neutral. "
        f"Overall sentiment is {overall_sentiment}."
    )

    return graph_path, description

# Function to fetch YouTube comments
def fetch_youtube_comments(url):
    video_id = url.split('v=')[-1]
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
    return comments

# Function to fetch Reddit comments
async def fetch_reddit_comments(url):
    reddit = await reddit_client()
    submission = await reddit.submission(url=url)
    await submission.comments.replace_more(limit=None)
    return [comment.body for comment in submission.comments.list()[:100]]

# Main function for Gradio
def analyze_sentiments(platform, url):
    if platform == "YouTube":
        comments = fetch_youtube_comments(url)
        graph, description = analyze_comments(comments, platform)
        return graph, description
    elif platform == "Reddit":
        comments = asyncio.run(fetch_reddit_comments(url))
        graph, description = analyze_comments(comments, platform)
        return graph, description
    else:
        return None, "Invalid platform."

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as interface:
    gr.Markdown("""
        # 📊 Unified Sentiment Analyzer
        Analyze sentiments from **YouTube** or **Reddit** comments with detailed visualizations and summaries.
        """)

    with gr.Row():
        with gr.Column(scale=1):
            platform = gr.Dropdown(["YouTube", "Reddit"], label="Select Platform", interactive=True)
            url = gr.Textbox(label="Enter URL", placeholder="Paste the YouTube or Reddit link here")

        with gr.Column(scale=2):
            output_image = gr.Image(label="Sentiment Distribution")
            output_description = gr.Textbox(label="Summary", interactive=False)

    analyze_btn = gr.Button("Analyze", elem_id="analyze-button")
    analyze_btn.click(analyze_sentiments, inputs=[platform, url], outputs=[output_image, output_description])

    gr.Markdown("""
        ### Tips:
        - For YouTube, ensure the video allows comments.
        - For Reddit, provide a valid post URL.
        """)

interface.launch()
