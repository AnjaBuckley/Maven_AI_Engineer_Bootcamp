import json
import os
from pathlib import Path

from openai import OpenAI

SUMMARIZE_TEXTS = [
    "This source provides a strategic roadmap for mastering n8n and AI automation by prioritizing foundational skills over flashy technology. The author emphasizes that learners must first master predictable, rule-based workflows and data structures like JSON and APIs before attempting to build complex AI agents. By understanding the transition curve of learning, students can navigate the inevitable periods of overwhelm and technical frustration. The guide also highlights the importance of process engineering, advising users to map out logic on paper to ensure high return on investment. Ultimately, the text encourages a shift from passive learning to active building, focusing on creating stable, scalable systems that solve real business problems.",
    "Our quarterly report showed revenue up 12 percent, churn down 3 percent, and a delayed migration due to staffing.",
]

SENTIMENT_TEXTS = [
    "The new dashboard is intuitive and significantly faster than before.",
    "The update broke key workflows and support has not responded in days.",
    "The document lists meeting times and project owners for next week.",
]


def summarize_prompt(version: str, text: str, max_length: int) -> str:
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


def sentiment_prompt(version: str, text: str) -> str:
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


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY before running this script.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    results = {"model": model, "summarize": [], "analyze_sentiment": []}

    for version in ["A", "B", "C"]:
        for text in SUMMARIZE_TEXTS:
            prompt = summarize_prompt(version, text, 50)
            response = client.responses.create(
                model=model, temperature=0.2, input=prompt
            )
            results["summarize"].append(
                {"prompt_version": version, "input": text, "output": response.output_text}
            )

    for version in ["A", "B", "C"]:
        for text in SENTIMENT_TEXTS:
            prompt = sentiment_prompt(version, text)
            response = client.responses.create(
                model=model, temperature=0.0, input=prompt
            )
            results["analyze_sentiment"].append(
                {"prompt_version": version, "input": text, "output": response.output_text}
            )

    out_path = Path("prompt_experiments_results.json")
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
