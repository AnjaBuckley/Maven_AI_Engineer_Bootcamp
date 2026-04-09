import json
import os
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field


app = FastAPI(title="FastAPI LLM Assignment API", version="1.0.0")


class HealthResponse(BaseModel):
    status: str
    timestamp: str


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to summarize")
    max_length: int = Field(
        120, ge=20, le=400, description="Maximum summary length in words"
    )
    prompt_version: Literal["A", "B", "C"] = "A"


class SummarizeResponse(BaseModel):
    summary: str
    prompt_version: str


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")
    prompt_version: Literal["A", "B", "C"] = "A"


class SentimentResponse(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    prompt_version: str


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured. Add it to your environment.",
        )
    return OpenAI(api_key=api_key)


def summarize_prompts(version: str, text: str, max_length: int) -> str:
    if version == "A":
        return (
            "Summarize the following text in plain English.\n"
            f"Hard limit: {max_length} words.\n"
            "Focus on the most important points only.\n\n"
            f"Text:\n{text}"
        )
    if version == "B":
        return (
            "You are an expert editor. Write a concise summary.\n"
            f"Constraints:\n- Maximum {max_length} words\n"
            "- Preserve key facts and outcomes\n"
            "- Avoid repetition and filler\n"
            "- Return only the final summary paragraph\n\n"
            f"Text:\n{text}"
        )
    return (
        "Example:\n"
        "Input: The team shipped two features, fixed five bugs, and delayed analytics.\n"
        "Output: The team released two features and fixed five bugs, while analytics work was postponed.\n\n"
        "Now summarize this input with the same style.\n"
        f"Limit: {max_length} words.\n"
        "Return only the summary.\n\n"
        f"Input:\n{text}"
    )


def sentiment_prompts(version: str, text: str) -> str:
    if version == "A":
        return (
            "Classify sentiment and return strict JSON.\n"
            'Schema: {"sentiment":"positive|negative|neutral","confidence":0.0-1.0,"explanation":"short reason"}\n'
            "Do not include markdown or extra text.\n\n"
            f"Text:\n{text}"
        )
    if version == "B":
        return (
            "Classify the sentiment using this rubric:\n"
            "- positive: overall favorable tone\n"
            "- negative: overall critical/unhappy tone\n"
            "- neutral: balanced, factual, or mixed without clear lean\n\n"
            "Then output strict JSON only with keys: sentiment, confidence, explanation.\n"
            "Confidence must be between 0 and 1.\n\n"
            f"Text:\n{text}"
        )
    return (
        "Few-shot examples:\n"
        'Text: "The app update is amazing and much faster."\n'
        'JSON: {"sentiment":"positive","confidence":0.95,"explanation":"Strong positive words like amazing and faster."}\n\n'
        'Text: "Support took forever and never solved my issue."\n'
        'JSON: {"sentiment":"negative","confidence":0.96,"explanation":"Clear dissatisfaction and unresolved problem."}\n\n'
        'Text: "The meeting starts at 10 and agenda is attached."\n'
        'JSON: {"sentiment":"neutral","confidence":0.9,"explanation":"Objective informational statement."}\n\n'
        "Now classify this text and return JSON only:\n"
        f"{text}"
    )


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok", timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(payload: SummarizeRequest) -> SummarizeResponse:
    client = get_openai_client()
    prompt = summarize_prompts(payload.prompt_version, payload.text, payload.max_length)

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2,
        input=prompt,
    )
    summary = response.output_text.strip()
    if not summary:
        raise HTTPException(status_code=502, detail="Model returned an empty summary.")

    return SummarizeResponse(summary=summary, prompt_version=payload.prompt_version)


@app.post("/analyze-sentiment", response_model=SentimentResponse)
def analyze_sentiment(payload: SentimentRequest) -> SentimentResponse:
    client = get_openai_client()
    prompt = sentiment_prompts(payload.prompt_version, payload.text)

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.0,
        input=prompt,
    )
    raw = response.output_text.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Model response was not valid JSON: {raw}",
        ) from exc

    sentiment = data.get("sentiment")
    confidence = data.get("confidence")
    explanation = data.get("explanation")
    if sentiment not in {"positive", "negative", "neutral"}:
        raise HTTPException(status_code=502, detail=f"Invalid sentiment: {sentiment}")
    if not isinstance(confidence, (float, int)) or not (0 <= confidence <= 1):
        raise HTTPException(status_code=502, detail=f"Invalid confidence: {confidence}")
    if not isinstance(explanation, str) or not explanation.strip():
        raise HTTPException(status_code=502, detail="Missing explanation.")

    return SentimentResponse(
        sentiment=sentiment,
        confidence=float(confidence),
        explanation=explanation.strip(),
        prompt_version=payload.prompt_version,
    )
