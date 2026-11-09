"""
Signal two: the style signal.

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures describe sentence-length spread, vocabulary repetition, and
punctuation density. `style_signal` combines their normalized values.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics
import unicodedata


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures ───────────────────────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies, normalized to 0–1.

    Returns:
        A float between 0 and 1. Higher means more sentence-length variation.

    The coefficient of variation is capped and scaled to this range.

    A text with fewer than two sentences returns 0.5, the neutral midpoint,
    because it provides no evidence about sentence-length variation.
    """
    lengths = [len(words(sentence)) for sentence in sentences(text)]
    if len(lengths) < 2:
        return 0.5

    mean_length = statistics.mean(lengths)
    if mean_length == 0:
        return 0.5

    coefficient_of_variation = statistics.stdev(lengths) / mean_length
    return min(coefficient_of_variation / 0.8, 1.0)


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to text length.

    Returns:
        A ratio from 0 to 1, using Unicode punctuation characters.
    """
    characters = [
        char for char in text
        if unicodedata.category(char).startswith("P")
    ]
    if not text:
        return 0.0
    return len(characters) / len(text)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Higher sentence-length spread and type-token ratio point more human,
         so each is inverted. Lower punctuation density points more AI-like.
      2. The normalized components are weighted 45% spread, 40% vocabulary
         repetition, and 15% punctuation sparseness.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.
    """
    tokens = words(text)
    if not tokens:
        return 0.5

    spread = sentence_length_spread(text)
    vocabulary_repetition = 1.0 - type_token_ratio(text)
    punctuation_sparseness = 1.0 - min(punctuation_density(text) / 0.08, 1.0)

    # Each component is normalized to 0–1, where higher means more AI-like.
    score = (
        0.45 * (1.0 - spread)
        + 0.40 * vocabulary_repetition
        + 0.15 * punctuation_sparseness
    )
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
