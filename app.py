from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class SentimentRequest(BaseModel):
    sentences: list[str]


# Broad positive vocabulary
POSITIVE = {
    "amazing", "awesome", "beautiful", "best", "brilliant",
    "celebrate", "celebrated", "cheerful", "delight",
    "delighted", "enjoy", "enjoyed", "enjoyable", "enjoying",
    "excellent", "excited", "exciting", "fantastic",
    "favourite", "favorite", "fun", "glad", "good",
    "great", "happy", "helpful", "impressive", "incredible",
    "inspiring", "joy", "joyful", "like", "liked", "likes",
    "love", "loved", "lovely", "outstanding", "perfect",
    "pleased", "positive", "pleasant", "recommend",
    "recommended", "reliable", "satisfied", "satisfying",
    "success", "successful", "superb", "terrific",
    "thank", "thanks", "thankful", "thrilled", "wonderful",
    "worthwhile", "win", "winner", "winning", "yay",
    "prosper", "prosperous", "grateful", "gratitude",
    "peaceful", "relieved", "relief", "comfortable",
    "convenient", "efficient", "improved", "improvement",
    "affordable", "smooth", "pleasantly", "positively"
}


# Broad negative vocabulary
NEGATIVE = {
    "abandon", "abandoned", "annoyed", "annoying", "anger",
    "angry", "awful", "bad", "badly", "broken", "confused",
    "confusing", "crash", "crashed", "damage", "damaged",
    "disappoint", "disappointed", "disappointing",
    "disappointment", "disaster", "disastrous", "dislike",
    "disliked", "fail", "failed", "failure", "fear",
    "frustrated", "frustrating", "frustration", "hate",
    "hated", "horrible", "hurt", "issue", "issues",
    "late", "lost", "loss", "miserable", "missing",
    "negative", "pain", "painful", "poor", "problem",
    "problems", "regret", "regretted", "rude", "sad",
    "scared", "terrible", "trouble", "unacceptable",
    "unhappy", "upset", "useless", "worst", "worse",
    "wrong", "worry", "worried", "waste", "wasted",
    "defective", "difficult", "difficulty", "expensive",
    "slow", "delay", "delayed", "complaint", "complaints",
    "disaster", "miserable", "horrendous", "dreadful",
    "disgusting", "disgusted", "furious", "mad",
    "irritated", "irritating", "regretful", "unpleasant",
    "inconvenient", "inconvenience", "broken", "failure"
}


# Strong multi-word expressions
POSITIVE_PHRASES = [
    "love this",
    "love it",
    "love the",
    "really good",
    "very good",
    "so good",
    "really great",
    "very great",
    "very happy",
    "really happy",
    "extremely happy",
    "very pleased",
    "really pleased",
    "highly recommend",
    "would recommend",
    "highly recommended",
    "well worth",
    "great experience",
    "good experience",
    "excellent experience",
    "best experience",
    "made my day",
    "couldn't be happier",
    "could not be happier",
    "works perfectly",
    "worked perfectly",
    "very satisfied",
    "really satisfied",
    "extremely satisfied",
    "very impressed",
    "really impressed",
    "pleasant experience",
    "great service",
    "excellent service",
    "thank you",
    "thanks a lot",
    "five stars",
    "5 stars"
]

NEGATIVE_PHRASES = [
    "hate this",
    "hate it",
    "really bad",
    "very bad",
    "so bad",
    "really terrible",
    "very terrible",
    "very disappointed",
    "really disappointed",
    "extremely disappointed",
    "very unhappy",
    "really unhappy",
    "very frustrated",
    "really frustrated",
    "very frustrating",
    "really frustrating",
    "terrible experience",
    "bad experience",
    "worst experience",
    "poor experience",
    "terrible service",
    "bad service",
    "poor service",
    "not good",
    "not great",
    "not happy",
    "not satisfied",
    "not worth",
    "waste of money",
    "waste of time",
    "total disaster",
    "complete disaster",
    "huge problem",
    "major problem",
    "doesn't work",
    "does not work",
    "didn't work",
    "did not work",
    "can't use",
    "cannot use",
    "never again"
]


NEGATIONS = {
    "not",
    "no",
    "never",
    "neither",
    "hardly",
    "barely",
    "isn't",
    "wasn't",
    "weren't",
    "don't",
    "doesn't",
    "didn't",
    "can't",
    "cannot",
    "couldn't",
    "won't",
    "wouldn't"
}


INTENSIFIERS = {
    "very",
    "really",
    "extremely",
    "absolutely",
    "incredibly",
    "so",
    "quite",
    "highly",
    "totally",
    "completely",
    "especially"
}


def get_sentiment(sentence: str) -> str:
    text = sentence.lower().strip()

    # Normalize apostrophes
    text = text.replace("’", "'")

    positive_score = 0.0
    negative_score = 0.0

    # Phrase matching
    for phrase in POSITIVE_PHRASES:
        if phrase in text:
            positive_score += 3

    for phrase in NEGATIVE_PHRASES:
        if phrase in text:
            negative_score += 3

    # Tokenize
    words = re.findall(r"[a-z']+", text)

    for i, word in enumerate(words):

        if word in POSITIVE:
            score = 1.0

            # Intensifier
            if i > 0 and words[i - 1] in INTENSIFIERS:
                score = 2.0

            # Check preceding 3 words for negation
            negated = any(
                w in NEGATIONS
                for w in words[max(0, i - 3):i]
            )

            if negated:
                negative_score += score
            else:
                positive_score += score

        elif word in NEGATIVE:
            score = 1.0

            if i > 0 and words[i - 1] in INTENSIFIERS:
                score = 2.0

            negated = any(
                w in NEGATIONS
                for w in words[max(0, i - 3):i]
            )

            if negated:
                positive_score += score
            else:
                negative_score += score

    # Strong sentiment indicators
    if "!" in text:
        if positive_score > negative_score:
            positive_score += 0.5
        elif negative_score > positive_score:
            negative_score += 0.5

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
