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
Held: 35
Broke: 21

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

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



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
