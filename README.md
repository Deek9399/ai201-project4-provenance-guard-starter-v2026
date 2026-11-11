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

1. A writer sends `POST /submit` with a `text` string and a `creator_id`.
2. `app.py::submit` checks that the JSON body and both fields are valid and
   rejects empty or oversized text before scoring.
3. `detector.model_signal` measures how predictable the text is to the local
   GPT-2 model and returns a 0–1 model score.
4. `stylometry.style_signal` measures surface features—sentence-length spread,
   vocabulary repetition, and punctuation—and returns a 0–1 style score.
5. `scoring.combine_signals` takes the equal-weight average of those scores.
6. `scoring.score_to_label` maps the combined score to `human`, `unsure`, or
   `ai`, along with the exact reader-facing sentence.
7. The service records the content ID, creator ID, both signal scores,
   combined score, guess, and label in the append-only audit log, then returns
   them in JSON. A writer can later send the content ID and their reasoning to
   `POST /appeal`; the appeal is appended to the log with status
   `under_review`, preserving the original decision.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** GPT-2 predictability, represented by `detector.model_signal`
on a 0–1 scale; higher scores mean the model finds the text more predictable.

**Why that might differ between human and AI writing:** Generated writing can
favor common, likely word sequences, which this model finds easier to predict.

**What it can't see:** Predictability does not establish authorship. Plain,
conventional human writing may also be predictable, while unusual human prose
may not be.

### Signal two — the style signal

**What it measures:** `stylometry.style_signal` combines sentence-length
variation, vocabulary repetition (one minus type-token ratio), and punctuation
sparseness. It returns 0–1, with higher scores meaning more AI-like.

**Why that might differ between human and AI writing:** Even sentence lengths,
repeated vocabulary, and sparse punctuation can appear in generated prose.

**What it can't see:** It cannot understand meaning or authorship. Editing,
quotes, typos, and text length can change its surface measurements without
changing who wrote the ideas.

### The combining rule

The combined score is the weighted mean of the model and style scores. Equal
weights mean a disagreement pulls the result toward the middle instead of
allowing either imperfect signal to decide alone. This is a score, not a
calibrated probability of AI authorship.

**The rule:** `(model_score + style_score) / 2`

**The numbers:** model weight `0.50`; style weight `0.50`. The style score uses
sentence spread `0.45`, vocabulary repetition `0.40`, and punctuation
sparseness `0.15`.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** On a
formal human-written paragraph, the model score was `0.5152` while the style
score was `0.1413`. Their equal-weight average was `0.3282`, between the two
signals and closer to the human side. This shows why neither signal should be
treated as proof of authorship.

**Four calibration examples (exploratory scores, not authorship proof):**

| Input | Model | Style | Combined |
|---|---:|---:|---:|
| Clearly AI-style garden proposal | 0.8186 | 0.5562 | 0.6874 |
| Clearly human tomato-garden story | 0.2974 | 0.1566 | 0.2270 |
| Formal human committee paragraph | 0.5152 | 0.1413 | 0.3282 |
| Lightly edited AI-style garden proposal | 0.7755 | 0.5542 | 0.6648 |



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00–0.35, inclusive | We think this was probably written by a person. |
| unsure | Above 0.35 and below 0.65 | We can't tell whether this was written by a person or AI. This estimate can be wrong. |
| high-confidence AI | 0.65–1.00, inclusive | This text has patterns often associated with AI-generated writing. This result is not proof of who wrote it. |

**Why I worded the "unsure" one this way:**
It admits the system cannot tell and explicitly notes that its estimate can be
wrong, rather than treating an uncertain score as an accusation.

**Label reachability check using real `/submit` requests:**

| Input | Combined score | Guess returned |
|---|---:|---|
| Human tomato-garden story | 0.2270 | `human` |
| Plain, conventional system description | 0.5224 | `unsure` |
| AI-style community-garden proposal | 0.6874 | `ai` |

---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

```bash
$ curl.exe -X POST http://127.0.0.1:5001/submit -H "Content-Type: application/json" -d '{\"text\": \"The committee reviewed the proposal in light of the available evidence; its members noted several practical advantages, but also identified costs that require further consideration. No final decision was reached.\", \"creator_id\": \"milestone6-demo\"}'
```

```json
{
  "combined_score": 0.3282,
  "confidence": 0.3282,
  "content_id": "17156163-b0f3-4783-9c88-efa5608015de",
  "guess": "human",
  "label": "We think this was probably written by a person.",
  "model_score": 0.5152,
  "style_score": 0.1413
}
```

`confidence` duplicates the combined score; it is not a calibrated probability.

**An appeal**

```bash
$ curl.exe -X POST http://127.0.0.1:5001/appeal -H "Content-Type: application/json" -d '{\"content_id\": \"17156163-b0f3-4783-9c88-efa5608015de\", \"reasoning\": \"I wrote this myself and would like a human review.\"}'
```

```json
{
  "content_id": "17156163-b0f3-4783-9c88-efa5608015de",
  "message": "Your appeal has been recorded for review.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl.exe "http://127.0.0.1:5001/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.3282,
      "content_id": "17156163-b0f3-4783-9c88-efa5608015de",
      "creator_id": "milestone6-demo",
      "guess": "human",
      "label": "We think this was probably written by a person.",
      "model_score": 0.5152,
      "style_score": 0.1413,
      "status": "decided",
      "timestamp": "2026-11-09T01:23:54+00:00"
    },
    {
      "content_id": "17156163-b0f3-4783-9c88-efa5608015de",
      "creator_id": "milestone6-demo",
      "event": "appeal",
      "reasoning": "I wrote this myself and would like a human review.",
      "status": "under_review",
      "timestamp": "2026-11-09T01:23:54+00:00"
    }
  ]
}
```

The service ran on port 5001 for this check to avoid a process already using
port 5000. The appeal is appended after the original decision, which remains in
the log unchanged.

---

## How I Used AI

**Moment 1**

- *What I asked for:* How to activate my Python virtual environment after
  `source .venv/bin/activate` failed in PowerShell.
- *What came back:* The PowerShell activation command,
  `.\.venv\Scripts\Activate.ps1`, and guidance to use a process-scoped
  execution-policy bypass only if script activation is blocked.
- *What I changed:* I used a separate Python 3.13 environment for this project
  after finding that its pinned dependencies do not support my Python 3.14
  environment, and verified it with `python test.py`.

**Moment 2**

- *What I asked for:* Help implementing the two signals, their combined score,
  reader-facing labels, and the appeal path for this project.
- *What came back:* A normalized style signal, an equal-weight combination
  rule, label wording and ranges, and an append-only appeal flow.
- *What I changed:* I checked the separate signal scores on four calibration
  examples, retained the formal-human disagreement as a documented limitation,
  and treated `confidence` as the combined score—not a calibrated probability.
  I also tested that all three labels are reachable and that appeals preserve
  the original audit entry.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 submissions per minute and 100 per day per creator ID.

**Why those numbers and not others:**
Five requests per minute allows a writer to make a few quick corrections but
stops a rapid burst from the same account; 100 per day leaves room for normal
use while limiting repeated probing. These are practical local-project limits,
not a guarantee against someone who can rotate creator IDs. The limiter uses
in-memory storage, so counts reset on restart.

**What a caller counts as:** The supplied `creator_id`; if it is missing or
invalid, the caller's IP address is used instead. This keeps separate writers
on one address from sharing a quota, but a client that invents new creator IDs
can get separate buckets.

**The run of status codes when I pushed past it:**

```powershell
python run_attacks.py --flood 15 --creator milestone8-flood-final --url http://127.0.0.1:5001
```

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

Ten of the 15 submissions were rejected. The generated report is
`results/flood_2026-11-10_2308.md`.

**Audit log check:** Three valid submissions and one request missing `text`
were sent. `GET /log?limit=100` returned 21 entries, including the three
decisions, the invalid-request rejection, and all 10 rate-limit rejections.
Every decision entry contained all nine required fields: timestamp,
content_id, creator_id, guess, model_score, style_score, combined_score,
label, and status. Here is the actual tail from `GET /log?limit=5`:

```json
{
  "count": 5,
  "entries": [
    {
      "creator_id": "milestone8-flood-final",
      "event": "rejected",
      "limit": "5 per 1 minute",
      "reason": "rate_limited",
      "status": "rejected",
      "timestamp": "2026-11-11T04:08:50+00:00"
    },
    {
      "combined_score": 0.5221,
      "content_id": "d269b93a-bf03-48e0-803a-865bca494ebc",
      "creator_id": "milestone8-log-final-1",
      "guess": "unsure",
      "label": "We can't tell whether this was written by a person or AI. This estimate can be wrong.",
      "model_score": 0.5977,
      "status": "decided",
      "style_score": 0.4464,
      "timestamp": "2026-11-11T04:09:00+00:00"
    },
    {
      "combined_score": 0.2275,
      "content_id": "a6c0dda1-0205-4a22-8fc0-3773a78e68a6",
      "creator_id": "milestone8-log-final-2",
      "guess": "human",
      "label": "We think this was probably written by a person.",
      "model_score": 0.2063,
      "status": "decided",
      "style_score": 0.2487,
      "timestamp": "2026-11-11T04:09:00+00:00"
    },
    {
      "combined_score": 0.4969,
      "content_id": "d702e265-daf9-45d5-b5d1-6f6a04bd7863",
      "creator_id": "milestone8-log-final-3",
      "guess": "unsure",
      "label": "We can't tell whether this was written by a person or AI. This estimate can be wrong.",
      "model_score": 0.6039,
      "status": "decided",
      "style_score": 0.3898,
      "timestamp": "2026-11-11T04:09:00+00:00"
    },
    {
      "creator_id": "milestone8-invalid-final",
      "event": "rejected",
      "reason": "invalid_text",
      "status": "rejected",
      "timestamp": "2026-11-11T04:09:00+00:00"
    }
  ]
}
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



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
