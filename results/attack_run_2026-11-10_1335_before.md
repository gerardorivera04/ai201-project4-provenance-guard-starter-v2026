# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-10 13:35
- Auto-marked BROKE (5xx, crash, no response): **2**
- Left for you to judge: **54**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

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
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_fbf5c9ce842e` | human | 0.305 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_03055f35a4a1` | human | 0.305 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_381c574d7417` | human | 0.305 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_a502a61e7ee2` | human | 0.305 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_c1c7d9963804` | human | 0.305 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 2 | 18 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_8a2de084c1b4",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.2512,
  "model_score": 0.1635,
  "style_score": 0.5852,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_746dcd811dd2",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.0932,
  "model_score": 0.5943,
  "style_score": 0.4989,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_da96807fde68",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.1896,
  "model_score": 0.6662,
  "style_score": 0.5234,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_0f59590318d4",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.1744,
  "model_score": 0.6114,
  "style_score": 0.563,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_4548c8314fb6",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.2116,
  "model_score": 0.3212,
  "style_score": 0.4673,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_9a8b97d195e0",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.0874,
  "model_score": 0.5727,
  "style_score": 0.5148,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_4cb2d0ba36ab",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.0048,
  "model_score": 0.5862,
  "style_score": 0.4089,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_9fc981311e49",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.1616,
  "model_score": 0.2452,
  "style_score": 0.5932,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_d61dd3479b45",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.2256,
  "model_score": 0.7042,
  "style_score": 0.5214,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_015430a3e52b",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.7782,
  "model_score": 0.9792,
  "style_score": 0.799,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_4ecec3fb01b4",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.2442,
  "model_score": 0.6175,
  "style_score": 0.6268,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_f47e0dc6f47b",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.4154,
  "model_score": 0.7387,
  "style_score": 0.6766,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_2d9a1185a5e4",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.4818,
  "model_score": 0.8051,
  "style_score": 0.6767,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_5909923dfc80",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.4494,
  "model_score": 0.8329,
  "style_score": 0.6164,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_b69a0fa3c96d",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.4854,
  "model_score": 0.8005,
  "style_score": 0.6849,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_ba394e7cbb8e",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.4966,
  "model_score": 0.8814,
  "style_score": 0.6153,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_5f7eb9cd2f4a",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.5318,
  "model_score": 0.8816,
  "style_score": 0.6502,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_b34795564eab",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.1118,
  "model_score": 0.3223,
  "style_score": 0.5659,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_8b1de00897f7",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.0184,
  "model_score": 0.4625,
  "style_score": 0.556,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_a5a6b5dc0ce0",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.3196,
  "model_score": 0.2044,
  "style_score": 0.4759,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_16f2f5bfa5ef",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.1758,
  "model_score": 0.5943,
  "style_score": 0.5815,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_783190dbc1b3",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.0522,
  "model_score": 0.4998,
  "style_score": 0.5524,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_6444ca0c5368",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.1222,
  "model_score": 0.6401,
  "style_score": 0.2377,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_631f770c4f65",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.1902,
  "model_score": 0.5583,
  "style_score": 0.6318,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>ValueError: Text is too short to score \u2014 a few sentences at least.\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes&a",
  "verdict": "BROKE"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_3d6a10079a03",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.3334,
  "model_score": 0.0,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_6b0b47ab1274",
  "creator_id": "attacker_MF04",
  "guess": "unsure",
  "confidence": 0.0112,
  "model_score": 0.0112,
  "style_score": 1.0,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_fb6f227697f2",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.6642,
  "model_score": 0.9976,
  "style_score": 0.6667,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_cff1f503f980",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.997,
  "model_score": 0.9969,
  "style_score": 1.0,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_4c95a73fbcdc",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.9064,
  "model_score": 0.9064,
  "style_score": 1.0,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "c_a5ecbdefdc90",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.8532,
  "model_score": 0.9876,
  "style_score": 0.8656,
  "label": "We think this was probably generated by AI.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "c_bdba74e2f86b",
  "creator_id": null,
  "guess": "unsure",
  "confidence": 0.0938,
  "model_score": 0.2395,
  "style_score": 0.6667,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "c_e7504573c00f",
  "creator_id": {
    "id": "x"
  },
  "guess": "unsure",
  "confidence": 0.2842,
  "model_score": 0.0492,
  "style_score": 0.6667,
  "label": "We cannot tell confidently whether this was written by a person or generated by AI.",
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 500,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;list&#39; object has no attribute &#39;get&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes",
  "verdict": "BROKE"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_fbf5c9ce842e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3046,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_03055f35a4a1",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3046,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_381c574d7417",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3046,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_a502a61e7ee2",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3046,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_c1c7d9963804",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.3046,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
