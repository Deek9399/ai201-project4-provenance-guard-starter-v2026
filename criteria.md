# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

Of 10 separate pieces of writing that I wrote myself, no more than 1 is labeled
high-confidence AI (combined score at or above 0.65) in each of three evaluation
trials.

**Why this target:**

I want to limit false accusations because a wrong accusation can harm a real
writer more than a missed AI-generated passage harms the site. Requiring the
target in all three trials checks that it is not just a lucky run.

---

## 2.

For five texts I identify as clearly AI-written and five I identify as clearly
human-written, the median combined score for the AI group is at least 0.20
higher than the median for the human group in each of three trials.

**Why this target:**

The score should separate these two groups by a visible margin, not merely put
them in a different order. A median makes the target less sensitive to one
unusually high or low score.

---

## 3.

When I submit a fixed set of at least nine calibration texts, at least one
submission receives each of the three guesses (`human`, `unsure`, and `ai`) in
each of three trials.

**Why this target:**

All three labels need to be reachable in practice; a label that exists only in
code is not useful to a reader. Repeating the same set checks that coverage is
not dependent on one run.

---

## 4.

For 10 appeals submitted with an existing `content_id`, every request returns
success, records an appeal event with that ID and the submitted reasoning, and
leaves the submission visibly marked `under_review` in the audit history.

**Why this target:**

An appeal is the writer's recourse when a judgment is wrong. Requiring both a
success response and a durable audit entry makes the outcome verifiable rather
than just reassuring the caller.

---

## 5.

Requests with missing, null, or empty `text`, and requests with more than 20,000
characters of text, receive a JSON 4xx response rather than a 5xx response.
After those four cases, `GET /health` still returns a successful response.

**Why this target:**

Malformed or oversized input should be rejected deliberately without crashing
the service. A health check afterward makes it observable that the service
survived the rejected requests.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
