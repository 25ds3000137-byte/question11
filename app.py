from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SentimentRequest(BaseModel):
    sentences: list[str]


POSITIVE = {
    "love", "loved", "lovely", "like", "liked", "likes",
    "good", "great", "excellent", "amazing", "awesome",
    "fantastic", "wonderful", "perfect", "best",
    "happy", "happiness", "enjoy", "enjoyed", "enjoying",
    "beautiful", "brilliant", "outstanding", "superb",
    "nice", "pleased", "delighted", "excited", "helpful",
    "satisfied", "satisfying", "impressive", "success",
    "successful", "win", "winner", "positive", "thank",
    "thanks", "thankful", "grateful", "recommend",
    "recommended", "worthwhile", "fun", "joy", "joyful",
    "pleasant", "easy", "efficient", "reliable", "improved",
    "improvement", "glad", "hopeful", "cheerful"
}

NEGATIVE = {
    "sad", "bad", "terrible", "horrible", "awful",
    "hate", "hated", "horrible", "worst", "angry",
    "disappointed", "disappointing", "upset", "poor",
    "failure", "failed", "fail", "pain", "unhappy",
    "annoyed", "annoying", "frustrated", "frustrating",
    "broken", "problem", "problems", "wrong", "error",
    "errors", "issue", "issues", "difficult", "hard",
    "useless", "waste", "wasted", "regret", "regretted",
    "negative", "badly", "slow", "expensive", "rude",
    "worried", "worry", "fear", "scared", "confusing",
    "confused", "dislike", "disliked", "fail", "failed",
    "delay", "delayed", "late", "missing", "lost",
    "damage", "damaged", "defective", "unacceptable"
}

NEGATIONS = {
    "not", "no", "never", "neither", "hardly", "barely",
    "isn't", "wasn't", "don't", "doesn't", "didn't",
    "can't", "cannot", "couldn't", "won't", "wouldn't"
}

INTENSIFIERS = {
    "very", "really", "extremely", "absolutely",
    "incredibly", "so", "quite", "highly", "totally",
    "completely"
}


def get_sentiment(sentence: str) -> str:
    text = sentence.lower()

    # Normalize punctuation while preserving apostrophes
    words = re.findall(r"[a-z']+", text)

    positive_score = 0.0
    negative_score = 0.0

    for i, word in enumerate(words):

        # Check whether the current word is negated
        negated = False
        for previous in words[max(0, i - 3):i]:
            if previous in NEGATIONS:
                negated = True
                break

        # Intensifier immediately before sentiment word
        multiplier = 1.0
        if i > 0 and words[i - 1] in INTENSIFIERS:
            multiplier = 1.5

        if word in POSITIVE:
            if negated:
                negative_score += multiplier
            else:
                positive_score += multiplier

        elif word in NEGATIVE:
            if negated:
                positive_score += multiplier
            else:
                negative_score += multiplier

    # Common strong phrases
    if any(phrase in text for phrase in [
        "love it",
        "love this",
        "love the",
        "highly recommend",
        "very happy",
        "really good",
        "really great",
        "very good",
        "very pleased"
    ]):
        positive_score += 2

    if any(phrase in text for phrase in [
        "hate it",
        "hate this",
        "very bad",
        "really bad",
        "very disappointed",
        "really disappointed",
        "very unhappy",
        "not good",
        "not happy",
        "not satisfied"
    ]):
        negative_score += 2

    if positive_score > negative_score:
        return "happy"

    if negative_score > positive_score:
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
