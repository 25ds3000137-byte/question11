from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SentimentRequest(BaseModel):
    sentences: list[str]


def get_sentiment(sentence: str) -> str:
    text = sentence.lower()

    happy_words = [
        "love", "love this", "great", "excellent", "amazing",
        "wonderful", "happy", "good", "awesome", "fantastic",
        "best", "enjoy", "enjoyed", "like", "liked", "perfect",
        "beautiful", "thank", "thanks", "delighted", "pleased"
    ]

    sad_words = [
        "sad", "terrible", "bad", "hate", "horrible",
        "awful", "worst", "angry", "disappointed", "disappointing",
        "upset", "poor", "failed", "failure", "pain",
        "unhappy", "annoyed", "frustrated", "broken", "problem"
    ]

    happy_score = sum(
        1 for word in happy_words
        if word in text
    )

    sad_score = sum(
        1 for word in sad_words
        if word in text
    )

    if happy_score > sad_score:
        return "happy"

    if sad_score > happy_score:
        return "sad"

    return "neutral"


@app.post("/sentiment")
async def sentiment(request: SentimentRequest):

    results = []

    for sentence in request.sentences:
        results.append({
            "sentence": sentence,
            "sentiment": get_sentiment(sentence)
        })

    return {
        "results": results
    }


@app.get("/")
async def root():
    return {"status": "ok"}
