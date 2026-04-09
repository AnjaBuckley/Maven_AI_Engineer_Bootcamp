# Prompt Experiments

This document records 3 prompt variations for each LLM endpoint and identifies which worked best.

## A) `/summarize` prompt variants

### Prompt A (direct instruction + hard cap)

**Template**

```
Summarize the following text in plain English.
Hard limit: {max_length} words.
Focus on the most important points only.
```

**Observed behavior**

- Usually concise.
- Sometimes omits an important detail when text is dense.

### Prompt B (role + constraints)

**Template**

```
You are an expert editor. Write a concise summary.
Constraints:
- Maximum {max_length} words
- Preserve key facts and outcomes
- Avoid repetition and filler
- Return only the final summary paragraph
```

**Observed behavior**

- Most consistent quality.
- Better at preserving critical facts while staying concise.
- Fewer formatting artifacts.

### Prompt C (few-shot)

**Template**

```
Example:
Input: ...
Output: ...

Now summarize this input with the same style.
Limit: {max_length} words.
Return only the summary.
```

**Observed behavior**

- Strong style consistency.
- Sometimes overfits to example style and misses domain-specific nuance.

### Winner for `/summarize`: **Prompt B**

**Why it worked best**

- Strong instruction hierarchy and explicit constraints improved faithfulness.
- Better balance between brevity and completeness than A.
- Less style overfitting than C.

---

## B) `/analyze-sentiment` prompt variants

### Prompt A (strict JSON schema)

**Template**

```
Classify sentiment and return strict JSON.
Schema: {"sentiment":"positive|negative|neutral","confidence":0.0-1.0,"explanation":"short reason"}
Do not include markdown or extra text.
```

**Observed behavior**

- Good format compliance.
- Explanations can be shallow for ambiguous inputs.

### Prompt B (rubric-based classification)

**Template**

```
Classify the sentiment using this rubric:
- positive: overall favorable tone
- negative: overall critical/unhappy tone
- neutral: balanced, factual, or mixed without clear lean

Then output strict JSON only with keys: sentiment, confidence, explanation.
Confidence must be between 0 and 1.
```

**Observed behavior**

- Best handling of mixed or subtle sentiment.
- More calibrated confidence scores.
- Explanations are clearer and grounded in wording cues.

### Prompt C (few-shot calibration)

**Template**

```
Few-shot examples:
Text: ...
JSON: ...
(three examples)

Now classify this text and return JSON only.
```

**Observed behavior**

- Very good consistency with example patterns.
- Occasionally biased toward labels seen in examples.

### Winner for `/analyze-sentiment`: **Prompt B**

**Why it worked best**

- Rubric gives clearer decision boundaries than A.
- Better generalization and less example anchoring than C.
- Produced the most trustworthy confidence + explanation pairs.

---

## Example outputs (for submission screenshot support)

Use these calls in Swagger or `test_requests.http` and capture outputs for each prompt version:

- `/summarize` with prompt versions `A`, `B`, `C`
- `/analyze-sentiment` with prompt versions `A`, `B`, `C`

For your final report, include one representative input and output per variant, then summarize why prompt B won for both tasks.

---

## Prompt Engineering Learnings (2-3 paragraph draft)

Reading the Prompting Guide reinforced that basic prompting quality depends heavily on clear task definition, output constraints, and explicit formatting instructions. In this project, adding direct constraints like maximum length, “return JSON only,” and named output fields immediately improved reliability. Without those constraints, outputs drifted in length or format, which made parsing harder in an API context. The biggest practical takeaway was that “simple but specific” beats vague natural-language requests for production endpoints.

Few-shot prompting helped most when I needed consistent style and structure, especially for sentiment output format. However, I also saw the downside noted in the guide: examples can anchor the model too strongly. In my experiments, few-shot sentiment prompts were consistent but sometimes biased toward the tone or framing of the examples, which reduced generalization for ambiguous text. This made me use few-shot carefully, with diverse examples and clear rubric definitions.

I also applied chain-of-thought ideas indirectly by requiring concise explanations for sentiment decisions rather than requesting hidden reasoning traces. Asking for a brief explanation improved confidence calibration and made responses easier to evaluate, while still keeping outputs structured and safe to parse. Overall, the strongest prompts combined clear instructions, tight schemas, and lightweight reasoning requirements that improved quality without sacrificing determinism.