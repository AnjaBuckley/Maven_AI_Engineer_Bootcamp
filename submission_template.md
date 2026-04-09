# Assignment Submission Template

## 1) Deployed API and Repository

- Render URL: `https://<your-render-service>.onrender.com`
- GitHub Repository: `https://github.com/<your-username>/<repo-name>`

## 2) Screenshots: All 3 Endpoints Working

Add screenshots that clearly show request + response for:

1. `GET /health`
2. `POST /summarize`
3. `POST /analyze-sentiment`

Tip: Use Render URL in Swagger docs (`/docs`) and capture full page with response JSON visible.

## 3) Prompt Variations and Best Choice

### `/summarize`

- Prompt A: direct instruction + hard word cap
- Prompt B: role + explicit constraints
- Prompt C: few-shot style example

Include one representative input/output for each prompt.

Best prompt: **B**

Why:

- Preserved key details better while staying within length constraints.
- Most consistent output quality across different inputs.

### `/analyze-sentiment`

- Prompt A: strict JSON schema instruction
- Prompt B: rubric-based decision boundaries
- Prompt C: few-shot sentiment examples

Include one representative input/output for each prompt.

Best prompt: **B**

Why:

- Better handling of mixed/ambiguous sentiment.
- More reliable confidence and explanation quality.

## 4) Prompt Engineering Reflection (2-3 paragraphs)

Reading the Prompting Guide showed that prompt quality improves significantly when tasks are explicit and outputs are tightly constrained. For this API, adding strict requirements such as maximum length, required JSON keys, and “return only JSON” reduced format drift and made endpoint responses easier to validate. Basic prompting worked best when the instruction order was clear: task first, constraints second, output format last.

Few-shot prompting improved consistency, especially for style and structure, but I observed that examples can bias outputs if they are not diverse. In sentiment analysis, few-shot prompts were reliable in formatting but sometimes too anchored to example phrasing. A rubric-based prompt generalized better by defining decision boundaries for positive, negative, and neutral classes, which improved confidence calibration.

The chain-of-thought section reinforced that reasoning structure matters, but for production APIs I used concise explanations instead of exposing long reasoning traces. Requiring a short explanation improved interpretability and quality checks without sacrificing predictability. Overall, the most effective prompts combined clear instructions, explicit constraints, and a lightweight reasoning requirement.