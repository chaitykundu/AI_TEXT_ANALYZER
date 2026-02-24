from textblob import TextBlob

def analyze_text(text: str):
    # Word count
    words = text.split()
    word_count = len(words)

    # Sentiment analysis
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "word_count": word_count,
        "sentiment": sentiment,
        "polarity_score": round(polarity, 3)
    }