# Narration guide (Kokoro TTS)

## Voice and speed
- Default `af_heart` (Kokoro's best-graded voice), speed 1.08. Others worth trying: `af_bella`,
  `bf_emma`, `am_michael`, `bm_george` (lower graded). Pass as `tts.py <voice> <speed>`.
- Don't exceed ~1.1 speed; cut words instead.

## Budget
- ~150 words/min including the 0.4 s gaps between beats. Count with:
  `python3 -c "from narration import SCENES; print(sum(len(b.split()) for s in SCENES.values() for b in s))"`
- 3–4 min ⇒ 480–580 words. The first draft of the example was 712 words (~5 min) and was cut to ~560.

## Structure (3b1b voice)
- Hook with a concrete image and a question, not a definition ("Every giant planet carries a
  record of its birth...").
- Name the paper and authors once, early, as the thing that answers the question.
- "Step one: ...", "Step two: ..." signposting; end each idea with its payoff ("Here's the payoff.").
- One number per sentence; say what it means ("About six and a half percent of its mass is metal").
- Save the most surprising result for near the end; finish with a recap and a forward look.
- Conversational connectors: "But", "So", "Now", "And here's the thing". Short sentences.

## Write for the ear
| Written | Say instead |
|---|---|
| HR 8799 | H R eighty-seven ninety-nine |
| AF Lep b | A F Lep b |
| CO, N₂, H₂O | C O, nitrogen, water |
| au | A U |
| M⊕ | Earth masses |
| x̄ | x bar |
| 10× | ten times |
| C/O | carbon to oxygen ratio |
| e.g., i.e., (asides) | rewrite as a full sentence |
- Commas create pauses: "Call it, x bar." puts weight on the symbol.
- Avoid symbols, slashes, parentheses and abbreviations entirely in narration text.
- If a word is mispronounced, respell it phonetically or swap the word.

## Beats
- One beat = one idea = one visual change, 4–14 s. Split long beats so the visuals can follow.
- A tiny final beat ("That excess becomes a measurable quantity.") is a good place for a boxed
  equation or key-number reveal.
