# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. **The caller sends JSON to `POST /submit`.** The request contains the
   submitted `text` and the `creator_id`; Flask receives the HTTP request.
2. **The route validates the request.** It checks that `text` is present and
   non-empty, keeps the creator identity, and creates a unique `content_id`
   for this submission.
3. **The model signal reads the text.** `detector.model_signal` runs the local
   language model, measures perplexity (predictability), and returns a
   0-to-1 AI-likelihood score.
4. **The style signal measures the text's shape.** `stylometry.style_signal`
   calculates sentence-length variation, vocabulary repetition, and
   punctuation density, then turns them into a second 0-to-1 AI-likelihood
   score without interpreting the topic.
5. **The scoring step combines the two scores.**
   `scoring.combine_signals` applies the documented weights; the result is one
   0-to-1 combined score where higher means more AI-like.
6. **The label step maps the score to a reader-facing result.**
   `scoring.score_to_label` produces a machine-readable guess (`human`,
   `unsure`, or `ai`) and a plain-English label using the human and AI
   thresholds.
7. **The service records and returns the decision.** `audit.log_decision`
   stores the content ID, creator, both signal scores, combined score, guess,
   label, and status. The JSON response gives the caller the same result so a
   reader can see the label and the writer can appeal by content ID.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the submitted text is to the local
language model, using perplexity. Low perplexity becomes a higher AI-likelihood
score because generated text often follows likely next-word patterns.

**Why that might differ between human and AI writing:** A model generates by
choosing likely continuations, so AI text can be smooth, ordinary, and easy for
another language model to predict. Human writing often includes personal,
unexpected wording or abrupt turns, which can raise perplexity.

**What it can't see:** It cannot see authorship or intent. Plain writing by a
real person, including a second-language writer's careful vocabulary, may be
just as predictable as AI writing and create a false positive. It also cannot
recognize that a human edited, paraphrased, or copied AI text.

### Signal two — the style signal

**What it measures:** The text's surface shape: how much sentence lengths vary,
how often words repeat (type-token ratio), and how dense or varied its
punctuation is. These measures are normalized and combined into a 0-to-1 score
where higher means more AI-like.

**Implementation:** `sentence_length_spread` is sentence-length standard
deviation divided by mean sentence length; `type_token_ratio` is unique words
divided by total words; and `punctuation_density` counts commas, semicolons,
colons, exclamation marks, question marks, em dashes, and hyphens per word.
The three AI-likelihood components are respectively
`1 / (1 + sentence_length_spread)`, `1 - type_token_ratio`, and
`1 - min(punctuation_density / 0.20, 1.0)`. The style score is their equal
average, rounded to four decimal places. Each component is therefore bounded
between 0 and 1, and higher always means more AI-like.

**Why that might differ between human and AI writing:** AI-generated prose
often settles into evenly sized sentences, repeated high-probability
vocabulary, and predictable punctuation. Human drafts tend to be lumpier,
with larger sentence-length changes, more individual word choices, and less
uniform punctuation.

**What it can't see:** It cannot read or understand meaning, facts, context,
or who wrote the text. A person can imitate an AI-like rhythm, and an AI text
can be made to look human by adding typos, splitting sentences, changing
punctuation, or inserting a quotation. Text length also affects vocabulary
ratios, so this signal cannot reliably compare pieces of very different
lengths without normalization.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** I use a weighted average of the model and style scores. When the
signals disagree, I treat the disagreement as uncertainty rather than letting
one signal alone make a high-confidence accusation.

**The numbers:** `0.50 * model_score + 0.50 * style_score`.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** A
plainly written human paragraph could receive `model_score = 0.80` because it
is highly predictable, while its varied sentence lengths and punctuation could
receive `style_score = 0.20`. The combined score is `0.50`, so the service
returns `unsure` instead of calling the writer's work AI with high confidence.
The 0.35 and 0.65 thresholds in `config.py` preserve that uncertainty band.

---

## False-Positive Trace

A real writer submits a clear, ordinary paragraph that they wrote themselves.
The model finds it very predictable and returns `model_score = 0.80`; the style
signal sees enough regularity to return `style_score = 0.64`. The combining rule
produces `0.72`, above the `0.65` AI threshold, so the reader sees the
high-confidence AI label even though the writer is human. That is the harmful
false positive this design is meant to limit. The writer can submit
`POST /appeal` with the returned `content_id` and a short explanation. The
service keeps the original decision, appends the appeal to the audit log, and
changes the item's status to `under_review`; it does not silently erase the
original result. A reviewer can then reconsider it. The wide unsure band and
the appeal path are the safeguards: they trade some missed AI text for fewer
wrong accusations.

---

## Endpoint Contracts

These are the contracts the route, signals, scoring, audit log, and client all
need to keep consistent.

### `POST /submit`

**Request JSON**

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `text` | string | yes | The writing to assess; it must not be empty or whitespace-only. |
| `creator_id` | string | yes | Stable identifier for the person submitting the writing. |

**Successful response JSON**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Unique ID used to find this submission and appeal it. |
| `creator_id` | string | The submitting creator ID. |
| `guess` | string | Exactly `human`, `unsure`, or `ai`. |
| `confidence` | number | `abs(combined_score - 0.50) * 2`, rounded to four decimals; 0 means the signals are exactly uncertain and 1 means maximum distance from the midpoint. |
| `label` | string | The exact plain-English message shown to the reader. |
| `model_score` | number | Detector signal, 0 to 1; higher means more AI-like. |
| `style_score` | number | Stylometry signal, 0 to 1; higher means more AI-like. |
| `combined_score` | number | Weighted result used for the label, 0 to 1. |
| `status` | string | Initially `decided`. |

**Error response:** Invalid or missing JSON, missing `text`, or blank `text`
returns HTTP `400` with `error` and `message` strings. A rate-limited request
returns HTTP `429` with `error`, `message`, and `limit`.

### `POST /appeal`

**Request JSON**

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `content_id` | string | yes | ID returned by `/submit`. |
| `reasoning` | string | yes | The writer's explanation of why the decision should be reviewed. |

**Successful response JSON**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | The appealed submission ID. |
| `status` | string | `under_review`, showing that the appeal was recorded. |
| `message` | string | Plain-English confirmation that the appeal was received. |

The endpoint verifies that `content_id` exists before recording the appeal.
Missing or blank fields return HTTP `400`; an unknown `content_id` returns HTTP
`404`. Every accepted appeal appends an audit entry and leaves the original
decision intact.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 through 0.35 | We think this was probably written by a person. |
| unsure | Above 0.35 and below 0.65 | We cannot tell confidently whether this was written by a person or generated by AI. |
| high-confidence AI | 0.65 through 1.00 | We think this was probably generated by AI. |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

It says what the service does not know instead of treating uncertainty as an
accusation. A score of exactly 0.35 receives the human label, and a score of
exactly 0.65 receives the AI label; scores between those boundaries receive the
unsure label.

## Four Calibration Inputs

| Input | Model signal | Style signal | Combined score | Result | Observation |
|---|---:|---:|---:|---|---|
| Clearly AI | 0.7441 | 0.3333 | 0.539 | Mixed evidence | The model signal was high, but the style signal was lower, so the two signals did not strongly agree. |
| Clearly human | 0.7624 | 0.6275 | 0.695 | Strong AI-like evidence | Both signals were relatively high, which demonstrates a serious false-positive risk for human writing. |
| Formal human writing | 0.5844 | 0.7193 | 0.652 | Strong AI-like evidence | The style signal was high, likely because the formal writing had regular structure and predictable wording. |
| Lightly-edited AI | 0.0764 | 0.6825 | 0.379 | Conflicting evidence | The model signal appeared human-like, while the style signal remained relatively AI-like after editing. |

The most important cases were formal human writing and lightly-edited AI.
Formal human writing produced strong AI-like evidence because its style score was
high. Lightly-edited AI produced conflicting evidence because its model and
style scores pointed in opposite directions. These results show why both
individual signal scores must be recorded alongside the combined score.

---

## Sample Run

**A submission**

```bash 1
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "I wrote this paragraph myself and kept notes while drafting it.", "creator_id": "writer-1"}'
```

```json (result) for submission 1
{
  "confidence": 0.5,
  "content_id": "c_f94d8874f5fc",
  "creator_id": "writer-1",
  "guess": "ai",
  "label": "We think this was probably generated by AI.",
  "model_score": 0.8,
  "style_score": 0.7,
  "combined_score": 0.75,
  "status": "decided"
}
```
```bash 2
curl -s -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text":"I wrote this paragraph myself while reviewing my project notes. I changed the second sentence after noticing that my first explanation was unclear.","creator_id":"writer-1"}'
```

```json (result) for submission 2
{
  "combined_score": 0.4812,
  "confidence": 0.0376,
  "content_id": "c_9bd2b7b86873",
  "creator_id": "writer-1",
  "guess": "unsure",
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "model_score": 0.3187,
  "status": "decided",
  "style_score": 0.6437
}
```

**An appeal**

```bash
$ curl -s -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id":"c_9bd2b7b86873","reasoning":"I wrote this submission myself while working on my project. I would like the original decision reviewed because the writing reflects my own notes and revisions."}'
```

```json (result)
{
  "content_id": "c_9bd2b7b86873",
  "message": "Your appeal was received and the submission is under review.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash 1
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```bash 2
$ curl -s "http://127.0.0.1:5000/log?limit=3" 
```

```json (result) for submission 1
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.75,
      "content_id": "c_f94d8874f5fc",
      "creator_id": "writer-1",
      "guess": "ai",
      "label": "We think this was probably generated by AI.",
      "model_score": 0.8,
      "status": "decided",
      "style_score": 0.7,
      "timestamp": "2026-11-03T18:19:18+00:00"
    },
    {
      "content_id": "c_f94d8874f5fc",
      "creator_id": "writer-1",
      "event": "appeal",
      "reasoning": "I wrote this submission myself and can provide drafting notes.",
      "status": "under_review",
      "timestamp": "2026-11-03T18:19:18+00:00"
    }
  ]
}
```

```json (result) for appeal to submission 2
{
  "count": 3,
  "entries": [
    {
      "combined_score": 0.6498,
      "content_id": "c_5ace0bc53798",
      "creator_id": "label-human",
      "guess": "unsure",
      "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
      "model_score": 0.5857,
      "status": "decided",
      "style_score": 0.7138,
      "timestamp": "2026-11-03T19:12:43+00:00"
    },
    {
      "combined_score": 0.4812,
      "content_id": "c_9bd2b7b86873",
      "creator_id": "writer-1",
      "guess": "unsure",
      "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
      "model_score": 0.3187,
      "status": "decided",
      "style_score": 0.6437,
      "timestamp": "2026-11-03T19:21:08+00:00"
    },
    {
      "content_id": "c_9bd2b7b86873",
      "creator_id": "writer-1",
      "event": "appeal",
      "reasoning": "I wrote this submission myself while working on my project. I would like the original decision reviewed because the writing reflects my own notes and revisions.",
      "status": "under_review",
      "timestamp": "2026-11-04T01:11:48+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked Claude's AI chat assistant on how I can combine the model and style signals, and convert the combined score into readable labels.   
- *What came back:* The AI tool made the suggestion to use a weighted average that used a calculation formula of taking the halves of both the model and signal scores, and sum those two values together. Additionally, there was a suggestion of implementating thresholds for my three label variants, which was 0.35 for human, 0.65 for AI, and an unsure label with a range between them. 
- *What I changed:* I implemented the combining rule in the scoring.py file and the three label outcomes in the same file with their respective functions, such as combine_signals and score_to_label. 

**Moment 2**

- *What I asked for:* I asked my AI tool to review the submission route for missing, empty, or confusing input and to explain what information should be recorded in the audit log. 
- *What came back:* The AI tool recommended validating 'text' as a non-empty string, preserving 'creator_id', generating a unique 'content_id', recording both signal scores and the final decision, and returning a clear error for invalid inputs.   
- *What I changed:* I added the validation and connected the route to the following components: detector, stylometry, signal, and scoring functions, audit logs, and JSON responses.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

Five submissions per minute gives a real writer enough leverage to submit drafts
or corrections without feeling blocked. Then, a daily limit of 50 allows legitimate
work across a day while making it difficult for a script to send hundreds or
thousands of variations to map the detector's thresholds.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

Requests are counted per `creator_id`. For example, if no valid creator ID is provided, the service falls back to the caller's remote address.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_8a2de084c1b4` | unsure | 0.251 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_746dcd811dd2` | unsure | 0.093 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_da96807fde68` | unsure | 0.190 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_0f59590318d4` | unsure | 0.174 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_4548c8314fb6` | unsure | 0.212 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_9a8b97d195e0` | unsure | 0.087 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_4cb2d0ba36ab` | unsure | 0.005 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `c_9fc981311e49` | unsure | 0.162 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_d61dd3479b45` | unsure | 0.226 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_015430a3e52b` | ai | 0.778 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_4ecec3fb01b4` | unsure | 0.244 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_f47e0dc6f47b` | ai | 0.415 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_2d9a1185a5e4` | ai | 0.482 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_5909923dfc80` | ai | 0.449 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_b69a0fa3c96d` | ai | 0.485 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_ba394e7cbb8e` | ai | 0.497 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_5f7eb9cd2f4a` | ai | 0.532 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `c_b34795564eab` | unsure | 0.112 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_8b1de00897f7` | unsure | 0.018 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_a5a6b5dc0ce0` | human | 0.320 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_16f2f5bfa5ef` | unsure | 0.176 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_783190dbc1b3` | unsure | 0.052 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_6444ca0c5368` | unsure | 0.122 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_631f770c4f65` | unsure | 0.190 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `c_3d6a10079a03` | human | 0.333 | HELD |
| MF04 | malformed | text is only punctuation | 200 | `c_6b0b47ab1274` | unsure | 0.011 | HELD |
| MF05 | malformed | text is a very long single word | 200 | `c_fb6f227697f2` | ai | 0.664 | HELD |
| MF06 | malformed | text is emoji only | 200 | `c_cff1f503f980` | ai | 0.997 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_4c95a73fbcdc` | ai | 0.906 | HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `c_a5ecbdefdc90` | ai | 0.853 | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `c_bdba74e2f86b` | unsure | 0.094 | BROKE |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 200 | `c_e7504573c00f` | unsure | 0.284 | BROKE |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_fbf5c9ce842e` | human | 0.305 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_03055f35a4a1` | human | 0.305 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_381c574d7417` | human | 0.305 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_a502a61e7ee2` | human | 0.305 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_c1c7d9963804` | human | 0.305 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

Total attacks: 56
Held: 37
Broke: 19

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
1. 
  {
    "timestamp": "2026-11-10T18:35:12+00:00",
    "content_id": "c_8a2de084c1b4",
    "creator_id": "attacker_EV01",
    "guess": "unsure",
    "model_score": 0.1635,
    "style_score": 0.5852,
    "combined_score": 0.3744,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "status": "decided"
  }
2. 
  {
    "timestamp": "2026-11-10T18:35:13+00:00",
    "content_id": "c_015430a3e52b",
    "creator_id": "attacker_EV10",
    "guess": "ai",
    "model_score": 0.9792,
    "style_score": 0.799,
    "combined_score": 0.8891,
    "label": "We think this was probably generated by AI.",
    "status": "decided"
  }
3. 
  {
    "timestamp": "2026-11-10T18:35:13+00:00",
    "content_id": "c_5f7eb9cd2f4a",
    "creator_id": "attacker_FP07",
    "guess": "ai",
    "model_score": 0.8816,
    "style_score": 0.6502,
    "combined_score": 0.7659,
    "label": "We think this was probably generated by AI.",
    "status": "decided"
  }
4. 
  {
    "timestamp": "2026-11-10T18:35:13+00:00",
    "content_id": "c_4ecec3fb01b4",
    "creator_id": "attacker_FP01",
    "guess": "unsure",
    "model_score": 0.6175,
    "style_score": 0.6268,
    "combined_score": 0.6221,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "status": "decided"
  }
5. 
  {
    "timestamp": "2026-11-10T18:35:14+00:00",
    "content_id": "c_6444ca0c5368",
    "creator_id": "attacker_PI05",
    "guess": "unsure",
    "model_score": 0.6401,
    "style_score": 0.2377,
    "combined_score": 0.4389,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "status": "decided"
  }
6. 
  {
    "timestamp": "2026-11-10T18:35:14+00:00",
    "content_id": "c_3d6a10079a03",
    "creator_id": "attacker_MF03",
    "guess": "human",
    "model_score": 0.0,
    "style_score": 0.6667,
    "combined_score": 0.3333,
    "label": "We think this was probably written by a person.",
    "status": "decided"
  }
7. 
  {
    "timestamp": "2026-11-10T18:35:14+00:00",
    "content_id": "c_bdba74e2f86b",
    "creator_id": "unknown",
    "guess": "unsure",
    "model_score": 0.2395,
    "style_score": 0.6667,
    "combined_score": 0.4531,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "status": "decided"
  }
8. 
  {
    "timestamp": "2026-11-10T18:35:14+00:00",
    "content_id": "c_e7504573c00f",
    "creator_id": {
      "id": "x"
    },
    "guess": "unsure",
    "model_score": 0.0492,
    "style_score": 0.6667,
    "combined_score": 0.3579,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "status": "decided"
  }
9. 
  {
    "timestamp": "2026-11-10T18:35:14+00:00",
    "content_id": "c_fbf5c9ce842e",
    "creator_id": "attacker_flood",
    "guess": "human",
    "model_score": 0.0287,
    "style_score": 0.6667,
    "combined_score": 0.3477,
    "label": "We think this was probably written by a person.",
    "status": "decided"
  }
10.
  {
    "timestamp": "2026-11-10T18:35:14+00:00",
    "creator_id": "attacker_flood",
    "event": "rejected",
    "status": "rejected",
    "reason": "rate_limited",
    "limit": "5 per 1 minute"
  }
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

FP07 - Human writing that repeats a phrase deliberately was the single worst outcome. First of all, the service labeled it 'ai' with a combined score of 0.7659. Furthermore, this is very harmful becuase the input represents genuine human writing, and the detector produced a high-confidence accusation rather than an uncertain result.  

---

## Before Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives — my own writing | ≤ 1 of 10 | 1/10 | 1/10 | 1/10 | MET |
| 2. Score spread — human versus AI comparison | ≥ 4/5 human below 0.35 and ≥ 4/5 AI above 0.65 | 0/5 and 0/5 | 0/5 and 0/5 | 0/5 and 0/5 | MISSED |
| 3. Label coverage — 15 varied submissions | 3 of 3 labels reachable | 1/3 | 1/3 | 1/3 | MISSED |
| 4. Appeal path submissions | 5 of 5 appeals pass | 5/5 | 5/5 | 5/5 | MET |
| 5. Bad input handling | 4 of 4 invalid requests return HTTP 400 | 3/4 | 3/4 | 3/4 | MISSED |

Criteria 1 was marked MET because each of the three trials produced exactly
1 false positive out of 10, which meets the target of no more than 1.
Criteria 4 was marked MET because all five appeal submissions passed in each
trial, including the required status change and preserved original decision.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

**NOTE: All the output below is from Trial 1.**

Produced by:
- File: `results/run_2026-11-10_2149_before.md`
- Functions: `run_eval.py::main`, `app.py::submit`, and `app.py::appeal`

```json

1. False positives - my own writing
[
  {
    "status": 200,
    "content_id": "c_567cc98f4e5c",
    "guess": "unsure",
    "confidence": 0.12,
    "model_score": 0.6198,
    "style_score": 0.5002,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Love can be both a blessing and a curse as viewed in William Shakespea"
  },
  {
    "status": 200,
    "content_id": "c_3e126d545fae",
    "guess": "unsure",
    "confidence": 0.2118,
    "model_score": 0.5817,
    "style_score": 0.6301,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Secondly, love can be interpreted as a destructive force as time progr"
  },
  {
    "status": 200,
    "content_id": "c_ad09c79117da",
    "guess": "unsure",
    "confidence": 0.0562,
    "model_score": 0.4067,
    "style_score": 0.6494,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I'm interested in working for CrowdStrike with the company's sharp eye"
  },
  {
    "status": 200,
    "content_id": "c_9b1dc1320bf2",
    "guess": "unsure",
    "confidence": 0.0174,
    "model_score": 0.5623,
    "style_score": 0.4551,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Therefore, I'm interested in working for CrowdStrike because CrowdStri"
  },
  {
    "status": 200,
    "content_id": "c_958d0927b401",
    "guess": "ai",
    "confidence": 0.4012,
    "model_score": 0.6855,
    "style_score": 0.7158,
    "label": "We think this was probably generated by AI.",
    "sent": "The purpose of this software design document is to introduce a new emp"
  },
  {
    "status": 200,
    "content_id": "c_b177948e45a8",
    "guess": "unsure",
    "confidence": 0.1892,
    "model_score": 0.4636,
    "style_score": 0.3472,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "CRUD - Create, read, update, and delete are the four basic functions o"
  },
  {
    "status": 200,
    "content_id": "c_b89b144ca3b5",
    "guess": "unsure",
    "confidence": 0.136,
    "model_score": 0.593,
    "style_score": 0.543,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I don\u2019t want to share much information, but I have a question. For con"
  },
  {
    "status": 200,
    "content_id": "c_b6b9ebd3dcb3",
    "guess": "unsure",
    "confidence": 0.1814,
    "model_score": 0.52,
    "style_score": 0.6613,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I want to create my own version of an AI Resume Tailor with scoring fu"
  },
  {
    "status": 200,
    "content_id": "c_90a1a5bb6b04",
    "guess": "unsure",
    "confidence": 0.2154,
    "model_score": 0.3618,
    "style_score": 0.4229,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "What questions should I ask at a NVIDIA event here at Georgia State as"
  },
  {
    "status": 200,
    "content_id": "c_20b980c585ca",
    "guess": "unsure",
    "confidence": 0.2032,
    "model_score": 0.7092,
    "style_score": 0.4939,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Which of the following services should he select on Home Depot's Pro R"
  }
]

2. Score spread - human versus AI comparison
[
  {
    "status": 200,
    "content_id": "c_a6885ddfd68c",
    "guess": "unsure",
    "confidence": 0.1946,
    "model_score": 0.6333,
    "style_score": 0.5613,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Can you make a draft of a business card for the company? For context, "
  },
  {
    "status": 200,
    "content_id": "c_05fc9c30f095",
    "guess": "unsure",
    "confidence": 0.0032,
    "model_score": 0.3869,
    "style_score": 0.6098,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "There's a section called Additional Details and is asking for the lega"
  },
  {
    "status": 200,
    "content_id": "c_407399478370",
    "guess": "unsure",
    "confidence": 0.1498,
    "model_score": 0.4874,
    "style_score": 0.3628,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "What are the steps in applying and registering as an LLC in Georgia? F"
  },
  {
    "status": 200,
    "content_id": "c_4a8421a1dcff",
    "guess": "unsure",
    "confidence": 0.1498,
    "model_score": 0.6413,
    "style_score": 0.5085,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Out of curiosity, does my father qualify for Social Security Disabilit"
  },
  {
    "status": 200,
    "content_id": "c_5eb913d88a67",
    "guess": "unsure",
    "confidence": 0.2082,
    "model_score": 0.6405,
    "style_score": 0.5677,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Video game development is an excellent profession for bringing passion"
  },
  {
    "status": 200,
    "content_id": "c_20e8753aafca",
    "guess": "unsure",
    "confidence": 0.2838,
    "model_score": 0.7544,
    "style_score": 0.5294,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "The importance of effective time management cannot be overstated in to"
  },
  {
    "status": 200,
    "content_id": "c_62670286f789",
    "guess": "human",
    "confidence": 0.5114,
    "model_score": 0.2556,
    "style_score": 0.233,
    "label": "We think this was probably written by a person.",
    "sent": "Absolutely. Given your current background\u2014CS coursework, Python/C/Java"
  },
  {
    "status": 200,
    "content_id": "c_d80c131f7cb6",
    "guess": "unsure",
    "confidence": 0.0736,
    "model_score": 0.5247,
    "style_score": 0.4016,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Ethernet can give you lower/more consistent latency, fewer connection "
  },
  {
    "status": 200,
    "content_id": "c_bddd486ecc41",
    "guess": "unsure",
    "confidence": 0.0764,
    "model_score": 0.3806,
    "style_score": 0.5431,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I contributed to software quality assurance in a fast-paced, agile env"
  },
  {
    "status": 200,
    "content_id": "c_9de21e05c8ce",
    "guess": "unsure",
    "confidence": 0.2626,
    "model_score": 0.3696,
    "style_score": 0.3678,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "StreetSense is an AI-assisted civic reporting app that lets residents "
  }
]

3. Label coverage - 15 varied submissions
[
  {
    "status": 200,
    "content_id": "c_44b3b0874571",
    "guess": "unsure",
    "confidence": 0.2142,
    "model_score": 0.6562,
    "style_score": 0.558,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I missed the bus this morning, so I walked the last few blocks to camp"
  },
  {
    "status": 200,
    "content_id": "c_d68af0166c42",
    "guess": "unsure",
    "confidence": 0.2482,
    "model_score": 0.6193,
    "style_score": 0.6289,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "My first attempt at the database query failed because I used the wrong"
  },
  {
    "status": 200,
    "content_id": "c_e17271d665c1",
    "guess": "unsure",
    "confidence": 0.0586,
    "model_score": 0.3815,
    "style_score": 0.6771,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I usually plan my week on Sunday night, but I do not follow the plan p"
  },
  {
    "status": 200,
    "content_id": "c_72abd9812370",
    "guess": "unsure",
    "confidence": 0.0654,
    "model_score": 0.5179,
    "style_score": 0.5474,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "The meeting started late because two people were still commuting. We u"
  },
  {
    "status": 200,
    "content_id": "c_2c940ef9490f",
    "guess": "unsure",
    "confidence": 0.0684,
    "model_score": 0.2838,
    "style_score": 0.6478,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I prefer testing small changes as I go instead of waiting until the en"
  },
  {
    "status": 200,
    "content_id": "c_b6f5c2c40d38",
    "guess": "unsure",
    "confidence": 0.0348,
    "model_score": 0.4515,
    "style_score": 0.5833,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "A reliable application should be easy to understand, simple to maintai"
  },
  {
    "status": 200,
    "content_id": "c_1671661e4537",
    "guess": "unsure",
    "confidence": 0.203,
    "model_score": 0.5701,
    "style_score": 0.6328,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "When I worked on the project, I learned that communication was almost "
  },
  {
    "status": 200,
    "content_id": "c_90f46e1b7487",
    "guess": "unsure",
    "confidence": 0.0606,
    "model_score": 0.4906,
    "style_score": 0.4488,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Good time management is not only about creating a schedule. It also re"
  },
  {
    "status": 200,
    "content_id": "c_b38649848c9b",
    "guess": "unsure",
    "confidence": 0.0728,
    "model_score": 0.3728,
    "style_score": 0.5543,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "The dashboard gives users a clear view of reported issues and their cu"
  },
  {
    "status": 200,
    "content_id": "c_ef25ffb9debd",
    "guess": "unsure",
    "confidence": 0.0656,
    "model_score": 0.2996,
    "style_score": 0.6348,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Learning a new framework can feel slow during the first few days becau"
  },
  {
    "status": 200,
    "content_id": "c_2ced3294058f",
    "guess": "unsure",
    "confidence": 0.1194,
    "model_score": 0.7173,
    "style_score": 0.4021,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "In today's rapidly evolving technological landscape, effective project"
  },
  {
    "status": 200,
    "content_id": "c_33f2c64bc610",
    "guess": "unsure",
    "confidence": 0.0048,
    "model_score": 0.5943,
    "style_score": 0.4105,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Artificial intelligence is transforming modern industries by improving"
  },
  {
    "status": 200,
    "content_id": "c_765624b67572",
    "guess": "unsure",
    "confidence": 0.0258,
    "model_score": 0.6081,
    "style_score": 0.4176,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "A successful cybersecurity strategy requires a comprehensive and proac"
  },
  {
    "status": 200,
    "content_id": "c_09d3d4a648df",
    "guess": "unsure",
    "confidence": 0.039,
    "model_score": 0.7971,
    "style_score": 0.242,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Cloud computing provides businesses with scalable, flexible, and cost-"
  },
  {
    "status": 200,
    "content_id": "c_650ffc769f05",
    "guess": "unsure",
    "confidence": 0.1828,
    "model_score": 0.8768,
    "style_score": 0.306,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "The development of a high-quality software application involves severa"
  }
]

4. Appeal path submissions
[
  {
    "status": 200,
    "content_id": "c_038209b336aa",
    "guess": "human",
    "confidence": 0.3152,
    "model_score": 0.0182,
    "style_score": 0.6667,
    "label": "We think this was probably written by a person.",
    "sent": "I wrote this short project reflection after completing my software tes",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  },
  {
    "status": 200,
    "content_id": "c_18ebc437a5c9",
    "guess": "unsure",
    "confidence": 0.0212,
    "model_score": 0.2864,
    "style_score": 0.6923,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "The application stores each report and allows users to review the curr",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  },
  {
    "status": 200,
    "content_id": "c_37c4c3cb0225",
    "guess": "human",
    "confidence": 0.3438,
    "model_score": 0.1561,
    "style_score": 0.5,
    "label": "We think this was probably written by a person.",
    "sent": "I tested the login flow, documented the failures, and shared the repro",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  },
  {
    "status": 200,
    "content_id": "c_284b840574d0",
    "guess": "unsure",
    "confidence": 0.0266,
    "model_score": 0.3599,
    "style_score": 0.6667,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "This paragraph describes how I improved the interface after receiving ",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  },
  {
    "status": 200,
    "content_id": "c_79660a3ea719",
    "guess": "unsure",
    "confidence": 0.2594,
    "model_score": 0.0482,
    "style_score": 0.6923,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I reviewed the final submission carefully and corrected the configurat",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  }
]

5. Bad input handling
[
  {
    "status": 400,
    "content_id": null,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_missing_text\"}"
  },
  {
    "status": 400,
    "content_id": null,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "content_id": null,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "   "
  },
  {
    "status": 200,
    "content_id": "c_ceb16dc0013a",
    "guess": "ai",
    "confidence": 0.6642,
    "model_score": 0.9976,
    "style_score": 0.6667,
    "label": "We think this was probably generated by AI.",
    "sent": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  }
]
```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->

1. Diagnosis for Criteria #2 - Criterion 2 missed in all three trials because the signal scores for the human and AI samples overlapped heavily. The main stage was the combining rule, with both signal stages contributing to the problem. The model signal did not consistently give human text low scores or AI text high scores, and the style signal also produced overlapping values for both groups. The combining rule average the two scores equally, so disagreements and middle-range scores were pulled toward the unsure band instead of separating the groups. As a result, 0 of 5 human samples were below 0.35 and 0 of 5 AI samples were above 0.65. Additionally, the mechanism was insufficient signal separation followed by averaging.

2. Diagnosis for Criteria #3 - Criterion 3 missed because the 15-submission sample produced only the unsure label. The primary stage was the combining rule, followed by label mapping. The model and style signals usually disagreed or produced middle-range values, and the equal-weight average placed every sample between 0.35 and 0.65. The label mapping did correctly covert those scores into unsure, so the mapping itself wasn't broken. Furthermore, the upstream scores never reached the human or the AI ranges. Finally, the mechanism was that the overlapping signal scores compress the combined scores into the unsure band, which made the human and the AI labels unreachable for that sample.

3. Diagnosis for Criteria #5 - Criterion 5 missed due to the oversized text request returing HTTP 200 instead of HTTP 400. Moreover, the stage was the route. For instance, the route checks whether text is a non-empty string, but it doesn't check the required maximum length of 10,000 characters. Therefore, the 10,001-character request passed validation and was sent through signal one, signal two, the combining rule, and label mapping, which produced a normal decision instead of an error. The mechanism was a missing maximum-length validation rule in the route.

Pattern found among the diagnoses: The detector's signals are not sufficiently separated. For example, signal one and signal two often produce middle-range or conflicting results. Then, the 0.50/0.50 combining rule compresses those results into the unsure band. Thus, this explains both Criterion 2's lack of separation and Criterion 3's missing human/AI labels. Furthermore, the false-positive attacks reveal the same root problem in reverse: predictable, formal, or repetitive human writing can make both signals appear AI-like.

**Broken Attacks**

1. The evasion failures followed one main pattern. EV01, EV02, EV03, EV06,
and EV07 targeted signal two by adding typos, changing sentence breaks,
adding quotations, varying sentence lengths, or padding punctuation. Signal
two measures surface shape rather than authorship, so those edits made
AI-generated text look more varied or less regular. The stage was signal two;
the mechanism was that human-like surface changes lowered the style signal
and dragged the combined score downward.

2. EV04 and EV08 targeted signal one. Unusual wording increased perplexity, and
short text reduced the amount of context available to the model. The stage
was signal one; the mechanism was that the model signal interpreted unusual
or insufficiently long text as less predictable and therefore more human-like.

3. EV05 and EV09 targeted both signals. Human editing or adding a human-written
opening changed both predictability and surface style. The stages were signal
one and signal two, with the combining rule amplifying the effect by averaging
the two lowered scores.

4. The false-positive failures FP02 through FP07 followed the opposite pattern.
The stage was primarily signal one and signal two, followed by the combining
rule. Formal structure, careful wording, technical documentation, templates,
and deliberate phrase repetition made genuine human writing predictable and
stylistically regular. Both signals therefore produced AI-like values, and
the equal-weight combining rule raised the final score enough to produce an
AI label. The mechanism was that the detector measures writing characteristics
that can also be produced by legitimate human writing; it cannot distinguish
formal or repetitive human authorship from AI authorship.

5. MF02 and RQ07 were route failures. MF02 caused a server error for a
single-character input, and RQ07 caused a server error for a JSON array
instead of returning a controlled client error. The route did not robustly
validate every accepted JSON shape before the scoring pipeline was called.

6. RQ02 and RQ06 were also route-validation failures. Missing or non-string
creator_id values were accepted instead of being rejected. The mechanism was
that the route validated text but did not enforce the creator_id contract.

---

## The Improvement

**What I changed:**

I changed the combining rule from an equal average to a weighted average:
`0.70 * model_score + 0.30 * style_score`. I also added route validation for
the required `creator_id`, JSON-object request shape, and the 10,000-character
text limit; rejected requests are recorded in the audit log.

**Which diagnosis pointed at it:**

The Criteria #2 and #3 diagnoses identified the equal-weight combining rule as
compressing conflicting signals into the unsure band. The Criteria #5
diagnosis identified the missing maximum-length check, and the malformed
request attacks exposed the missing object and `creator_id` validation.

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

The After run used the same 56 attacks as the Before run. The complete result
table is recorded in
`results/attack_run_2026-11-11_0027_after.md`; the key comparison is:

| Result | Before | After |
|---|---:|---:|
| Total attacks | 56 | 56 |
| Automatic crashes | 3 | 0 |
| Held | 37 | 37 |
| Broke | 19 | 19 |
| Single-character input | 500 | 400 |
| Oversized input | 200 | 400 |
| Missing `creator_id` | 200 | 400 |
| JSON array body | 500 | 400 |
| Flood limit | 429 after five accepted | 429 after five accepted |

The After attack table follows the same format as the Before table:

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_39f911a4e0f5` | human | 0.420 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_ad94df5b453e` | unsure | 0.131 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_4854f521a7ba` | unsure | 0.247 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_29c3d67eebd5` | unsure | 0.194 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_40564059f3ea` | unsure | 0.270 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_7aa0f3b106ca` | unsure | 0.111 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_d0643d46adb8` | unsure | 0.066 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `c_6bcb4bd5a7c1` | human | 0.301 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_3dcec372880c` | unsure | 0.299 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_b72f9f14c62b` | ai | 0.850 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_353c6cf2916f` | unsure | 0.241 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_29657a9cd0f9` | ai | 0.440 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_7808f9f3e722` | ai | 0.533 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_4e94c5cd0a70` | ai | 0.536 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_783f527d1955` | ai | 0.532 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_91aedf5d881c` | ai | 0.603 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_9973a56682c8` | ai | 0.624 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `c_93a81cb3bbfd` | unsure | 0.209 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_a35793653f3f` | unsure | 0.019 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_3901f6058fcd` | human | 0.428 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_a3a758f441d2` | unsure | 0.181 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_17fd04b73934` | unsure | 0.031 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_dbd15d706f79` | unsure | 0.039 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_ddf4ec0bcdda` | unsure | 0.161 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `c_cb4569eae349` | human | 0.600 | HELD |
| MF04 | malformed | text is only punctuation | 200 | `c_306b0bbf42e5` | human | 0.384 | HELD |
| MF05 | malformed | text is a very long single word | 200 | `c_5697013d3175` | ai | 0.797 | HELD |
| MF06 | malformed | text is emoji only | 200 | `c_3cd8dda86254` | ai | 0.996 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_b37d11e232e5` | ai | 0.869 | HELD |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_03905a9a3954` | human | 0.560 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_1c1a25c139fb` | human | 0.560 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_9102752e8b4d` | human | 0.560 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_86e8f5c781de` | human | 0.560 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_84a3f3d7f56e` | human | 0.560 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

**Ten After audit log entries from the run**

```json
1. {"timestamp":"2026-11-11T05:27:47+00:00","content_id":"c_39f911a4e0f5","creator_id":"attacker_EV01","guess":"human","model_score":0.1635,"style_score":0.5852,"combined_score":0.29,"status":"decided"}
2. {"timestamp":"2026-11-11T05:27:48+00:00","content_id":"c_b72f9f14c62b","creator_id":"attacker_EV10","guess":"ai","model_score":0.9792,"style_score":0.799,"combined_score":0.9251,"status":"decided"}
3. {"timestamp":"2026-11-11T05:27:48+00:00","content_id":"c_9973a56682c8","creator_id":"attacker_FP07","guess":"ai","model_score":0.8816,"style_score":0.6502,"combined_score":0.8122,"status":"decided"}
4. {"timestamp":"2026-11-11T05:27:49+00:00","creator_id":"attacker_MF02","event":"rejected","status":"rejected","reason":"invalid_text"}
5. {"timestamp":"2026-11-11T05:27:49+00:00","creator_id":"attacker_MF08","event":"rejected","status":"rejected","reason":"text_too_long","max_length":10000}
6. {"timestamp":"2026-11-11T05:27:49+00:00","creator_id":"unknown","event":"rejected","status":"rejected","reason":"invalid_creator_id"}
7. {"timestamp":"2026-11-11T05:27:49+00:00","creator_id":"unknown","event":"rejected","status":"rejected","reason":"invalid_json_object"}
8. {"timestamp":"2026-11-11T05:27:49+00:00","content_id":"c_03905a9a3954","creator_id":"attacker_flood","guess":"human","model_score":0.0287,"style_score":0.6667,"combined_score":0.2201,"status":"decided"}
9. {"timestamp":"2026-11-11T05:27:49+00:00","creator_id":"attacker_flood","event":"rejected","status":"rejected","reason":"rate_limited","limit":"5 per 1 minute"}
10. {"timestamp":"2026-11-11T05:27:48+00:00","content_id":"c_353c6cf2916f","creator_id":"attacker_FP01","guess":"unsure","model_score":0.6175,"style_score":0.6268,"combined_score":0.6203,"status":"decided"}
```

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

The change helped the route-related objective: automatic attack crashes fell
from 3 to 0, and the bad-input criterion improved from 3/4 to 4/4 in every
trial. The scoring change did not meet the separation target: Criterion #2
remained 0/5 human and 0/5 AI, while Criterion #3 improved from 1/3 to 2/3
labels because an AI label became reachable, but the 15-submission sample
still contained no human label. Criteria #1 and #4 stayed at their original
passing results.

### After Run Log and Verdicts

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives — my own writing | ≤ 1 of 10 | 1/10 | 1/10 | 1/10 | MET |
| 2. Score spread — human versus AI comparison | ≥ 4/5 human below 0.35 and ≥ 4/5 AI above 0.65 | 0/5 and 0/5 | 0/5 and 0/5 | 0/5 and 0/5 | MISSED |
| 3. Label coverage — 15 varied submissions | 3 of 3 labels reachable | 2/3 | 2/3 | 2/3 | MISSED |
| 4. Appeal path submissions | 5 of 5 appeals pass | 5/5 | 5/5 | 5/5 | MET |
| 5. Bad input handling | 4 of 4 invalid requests return HTTP 400 | 4/4 | 4/4 | 4/4 | MET |

Produced by:
- File: `results/run_2026-11-11_0029_after.md`
- Functions: `run_eval.py::main`, `app.py::submit`, and `app.py::appeal`

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

**NOTE: All the output below is from Trial 1.**

```json

1. False positives - my own writing
[
  {
    "status": 200,
    "content_id": "c_96d746ff67a6",
    "guess": "unsure",
    "confidence": 0.1678,
    "model_score": 0.6198,
    "style_score": 0.5002,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Love can be both a blessing and a curse as viewed in William Shakespea"
  },
  {
    "status": 200,
    "content_id": "c_5510eaf46e6b",
    "guess": "unsure",
    "confidence": 0.1924,
    "model_score": 0.5817,
    "style_score": 0.6301,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Secondly, love can be interpreted as a destructive force as time progr"
  },
  {
    "status": 200,
    "content_id": "c_a6946a5812bb",
    "guess": "unsure",
    "confidence": 0.041,
    "model_score": 0.4067,
    "style_score": 0.6494,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I'm interested in working for CrowdStrike with the company's sharp eye"
  },
  {
    "status": 200,
    "content_id": "c_a2c40aeafa5f",
    "guess": "unsure",
    "confidence": 0.0602,
    "model_score": 0.5623,
    "style_score": 0.4551,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Therefore, I'm interested in working for CrowdStrike because CrowdStri"
  },
  {
    "status": 200,
    "content_id": "c_841d88c04b06",
    "guess": "ai",
    "confidence": 0.3892,
    "model_score": 0.6855,
    "style_score": 0.7158,
    "label": "We think this was probably generated by AI.",
    "sent": "The purpose of this software design document is to introduce a new emp"
  },
  {
    "status": 200,
    "content_id": "c_2931cc1b0ad2",
    "guess": "unsure",
    "confidence": 0.1426,
    "model_score": 0.4636,
    "style_score": 0.3472,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "CRUD - Create, read, update, and delete are the four basic functions o"
  },
  {
    "status": 200,
    "content_id": "c_d2ef19272074",
    "guess": "unsure",
    "confidence": 0.156,
    "model_score": 0.593,
    "style_score": 0.543,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I don\u2019t want to share much information, but I have a question. For con"
  },
  {
    "status": 200,
    "content_id": "c_a63a87e4b7f3",
    "guess": "unsure",
    "confidence": 0.1248,
    "model_score": 0.52,
    "style_score": 0.6613,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I want to create my own version of an AI Resume Tailor with scoring fu"
  },
  {
    "status": 200,
    "content_id": "c_8d8b25400298",
    "guess": "unsure",
    "confidence": 0.2398,
    "model_score": 0.3618,
    "style_score": 0.4229,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "What questions should I ask at a NVIDIA event here at Georgia State as"
  },
  {
    "status": 200,
    "content_id": "c_e77c04d3cdba",
    "guess": "unsure",
    "confidence": 0.2892,
    "model_score": 0.7092,
    "style_score": 0.4939,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Which of the following services should he select on Home Depot's Pro R"
  }
]

2. Score range - human versus AI comparison
[
  {
    "status": 200,
    "content_id": "c_55aa539d0492",
    "guess": "unsure",
    "confidence": 0.2234,
    "model_score": 0.6333,
    "style_score": 0.5613,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Can you make a draft of a business card for the company? For context, "
  },
  {
    "status": 200,
    "content_id": "c_200920380a38",
    "guess": "unsure",
    "confidence": 0.0924,
    "model_score": 0.3869,
    "style_score": 0.6098,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "There's a section called Additional Details and is asking for the lega"
  },
  {
    "status": 200,
    "content_id": "c_b0c88f9207f5",
    "guess": "unsure",
    "confidence": 0.1,
    "model_score": 0.4874,
    "style_score": 0.3628,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "What are the steps in applying and registering as an LLC in Georgia? F"
  },
  {
    "status": 200,
    "content_id": "c_03ade1a911d5",
    "guess": "unsure",
    "confidence": 0.203,
    "model_score": 0.6413,
    "style_score": 0.5085,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Out of curiosity, does my father qualify for Social Security Disabilit"
  },
  {
    "status": 200,
    "content_id": "c_0f27db0a1758",
    "guess": "unsure",
    "confidence": 0.2374,
    "model_score": 0.6405,
    "style_score": 0.5677,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Video game development is an excellent profession for bringing passion"
  },
  {
    "status": 200,
    "content_id": "c_550f1df4e149",
    "guess": "ai",
    "confidence": 0.3738,
    "model_score": 0.7544,
    "style_score": 0.5294,
    "label": "We think this was probably generated by AI.",
    "sent": "The importance of effective time management cannot be overstated in to"
  },
  {
    "status": 200,
    "content_id": "c_5daadc95176d",
    "guess": "human",
    "confidence": 0.5024,
    "model_score": 0.2556,
    "style_score": 0.233,
    "label": "We think this was probably written by a person.",
    "sent": "Absolutely. Given your current background\u2014CS coursework, Python/C/Java"
  },
  {
    "status": 200,
    "content_id": "c_fab2195b6c3b",
    "guess": "unsure",
    "confidence": 0.0244,
    "model_score": 0.5247,
    "style_score": 0.4016,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Ethernet can give you lower/more consistent latency, fewer connection "
  },
  {
    "status": 200,
    "content_id": "c_3b9d9c9b9eb9",
    "guess": "unsure",
    "confidence": 0.1412,
    "model_score": 0.3806,
    "style_score": 0.5431,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I contributed to software quality assurance in a fast-paced, agile env"
  },
  {
    "status": 200,
    "content_id": "c_54cdcba6d70e",
    "guess": "unsure",
    "confidence": 0.2618,
    "model_score": 0.3696,
    "style_score": 0.3678,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "StreetSense is an AI-assisted civic reporting app that lets residents "
  }
]

3. Labeled coverage - 15 varied submissions
[
  {
    "status": 200,
    "content_id": "c_665be5e541aa",
    "guess": "unsure",
    "confidence": 0.2534,
    "model_score": 0.6562,
    "style_score": 0.558,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I missed the bus this morning, so I walked the last few blocks to camp"
  },
  {
    "status": 200,
    "content_id": "c_3a7169f86db3",
    "guess": "unsure",
    "confidence": 0.2444,
    "model_score": 0.6193,
    "style_score": 0.6289,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "My first attempt at the database query failed because I used the wrong"
  },
  {
    "status": 200,
    "content_id": "c_285faec0b4f0",
    "guess": "unsure",
    "confidence": 0.0596,
    "model_score": 0.3815,
    "style_score": 0.6771,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I usually plan my week on Sunday night, but I do not follow the plan p"
  },
  {
    "status": 200,
    "content_id": "c_fa8fd29d4da8",
    "guess": "unsure",
    "confidence": 0.0536,
    "model_score": 0.5179,
    "style_score": 0.5474,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "The meeting started late because two people were still commuting. We u"
  },
  {
    "status": 200,
    "content_id": "c_1f2ffcc8bb1c",
    "guess": "unsure",
    "confidence": 0.214,
    "model_score": 0.2838,
    "style_score": 0.6478,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "I prefer testing small changes as I go instead of waiting until the en"
  },
  {
    "status": 200,
    "content_id": "c_6c3e574c049e",
    "guess": "unsure",
    "confidence": 0.018,
    "model_score": 0.4515,
    "style_score": 0.5833,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "A reliable application should be easy to understand, simple to maintai"
  },
  {
    "status": 200,
    "content_id": "c_b38fe288fed6",
    "guess": "unsure",
    "confidence": 0.1778,
    "model_score": 0.5701,
    "style_score": 0.6328,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "When I worked on the project, I learned that communication was almost "
  },
  {
    "status": 200,
    "content_id": "c_2a601c103da0",
    "guess": "unsure",
    "confidence": 0.0438,
    "model_score": 0.4906,
    "style_score": 0.4488,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Good time management is not only about creating a schedule. It also re"
  },
  {
    "status": 200,
    "content_id": "c_010c68386508",
    "guess": "unsure",
    "confidence": 0.1454,
    "model_score": 0.3728,
    "style_score": 0.5543,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "The dashboard gives users a clear view of reported issues and their cu"
  },
  {
    "status": 200,
    "content_id": "c_b53cbe3f02aa",
    "guess": "unsure",
    "confidence": 0.1996,
    "model_score": 0.2996,
    "style_score": 0.6348,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Learning a new framework can feel slow during the first few days becau"
  },
  {
    "status": 200,
    "content_id": "c_5b70556dfef1",
    "guess": "unsure",
    "confidence": 0.2454,
    "model_score": 0.7173,
    "style_score": 0.4021,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "In today's rapidly evolving technological landscape, effective project"
  },
  {
    "status": 200,
    "content_id": "c_4e26c468dce0",
    "guess": "unsure",
    "confidence": 0.0784,
    "model_score": 0.5943,
    "style_score": 0.4105,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Artificial intelligence is transforming modern industries by improving"
  },
  {
    "status": 200,
    "content_id": "c_0e359661fedb",
    "guess": "unsure",
    "confidence": 0.1018,
    "model_score": 0.6081,
    "style_score": 0.4176,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "A successful cybersecurity strategy requires a comprehensive and proac"
  },
  {
    "status": 200,
    "content_id": "c_fdce05b9dcc6",
    "guess": "unsure",
    "confidence": 0.2612,
    "model_score": 0.7971,
    "style_score": 0.242,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "Cloud computing provides businesses with scalable, flexible, and cost-"
  },
  {
    "status": 200,
    "content_id": "c_3fd1dc8692bb",
    "guess": "ai",
    "confidence": 0.4112,
    "model_score": 0.8768,
    "style_score": 0.306,
    "label": "We think this was probably generated by AI.",
    "sent": "The development of a high-quality software application involves severa"
  }
]

4. Appeal path submissions
[
  {
    "status": 200,
    "content_id": "c_6df184008baa",
    "guess": "human",
    "confidence": 0.5746,
    "model_score": 0.0182,
    "style_score": 0.6667,
    "label": "We think this was probably written by a person.",
    "sent": "I wrote this short project reflection after completing my software tes",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  },
  {
    "status": 200,
    "content_id": "c_8b44633f31a0",
    "guess": "unsure",
    "confidence": 0.1836,
    "model_score": 0.2864,
    "style_score": 0.6923,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "The application stores each report and allows users to review the curr",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  },
  {
    "status": 200,
    "content_id": "c_0f15e246ecb6",
    "guess": "human",
    "confidence": 0.4814,
    "model_score": 0.1561,
    "style_score": 0.5,
    "label": "We think this was probably written by a person.",
    "sent": "I tested the login flow, documented the failures, and shared the repro",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  },
  {
    "status": 200,
    "content_id": "c_ab43874aa56a",
    "guess": "unsure",
    "confidence": 0.0962,
    "model_score": 0.3599,
    "style_score": 0.6667,
    "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
    "sent": "This paragraph describes how I improved the interface after receiving ",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  },
  {
    "status": 200,
    "content_id": "c_5b80f749bede",
    "guess": "human",
    "confidence": 0.5172,
    "model_score": 0.0482,
    "style_score": 0.6923,
    "label": "We think this was probably written by a person.",
    "sent": "I reviewed the final submission carefully and corrected the configurat",
    "appeal_http_status": 200,
    "appeal_status": "under_review",
    "appeal_audit_entries": 1,
    "original_decision_preserved": true,
    "appeal_pass": true
  }
]

5. Bad input handling
[
  {
    "status": 400,
    "content_id": null,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_missing_text\"}"
  },
  {
    "status": 400,
    "content_id": null,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "content_id": null,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "   "
  },
  {
    "status": 400,
    "content_id": null,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  }
]
```

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

The following attacks still occur:

- **EV01 (typos), EV02 (broken-up sentences), EV03 (pasted quotation), EV06
  (extreme sentence lengths), and EV07 (punctuation padding):** I would add
  features that discount edit noise and quotations before calculating the
  surface-shape signal, then calibrate those features against held-out human
  and AI samples. I stopped after the one permitted controlled weight change;
  changing the signal features and the weights together would not isolate the
  experiment's effect.
- **EV04 (unusual words):** I would make the model signal less sensitive to
  isolated rare words by evaluating the text in multiple windows and combining
  the window scores. I stopped for the same reason: the experiment allowed one
  controlled weight change, not a simultaneous detector redesign.
- **EV05 (heavy human editing):** I would compare the model and style signals
  across chunks and flag a large disagreement for review instead of allowing
  the combined score to settle in a human or unsure band. I stopped after the
  required single change so that I would not claim evidence from an unmeasured
  second intervention.
- **EV08 (text below the token window):** I would reject or separately label
  submissions too short for a reliable model-signal decision, or use a
  shorter-text calibration set. I stopped because adding a length policy would
  change the input-validation behavior beyond the controlled scoring change.
- **EV09 (AI text with a human opening):** I would score multiple sections and
  require agreement across them, rather than letting a human-looking opening
  offset the rest of the text. I stopped after the one controlled weight
  change, so sectioning and recalibration were outside this run.
- **FP02 (formal human writing), FP03 (careful non-native writing), FP04
  (rubric-written essay), FP05 (technical documentation), FP06 (formal
  template imitation), and FP07 (deliberate phrase repetition):** I would
  expand the human calibration set with these writing styles and lower the
  style signal's influence when it is the only strong AI-like evidence. I
  stopped after the controlled weight change rather than tuning thresholds
  and calibration data at the same time.

Criterion #2 remains unmet: it scored 0/5 for human samples and 0/5 for AI
samples. Criterion #3 improved to 2/3 because the AI label became reachable,
but its 15-submission sample still contained no human label, so the sample
portion remains unmet. Criteria #1 and #4 passed, and the bad-input result
improved to 4/4; I did not make further changes because the experiment design
required stopping after one controlled weight change.


**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

In production, I would prefer a wider unsure outcome over a high-confidence
accusation when the signals disagree, even though that lets some AI text pass.
The system and reviewers pay through additional manual review, while writers
pay less for false accusations.


<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
