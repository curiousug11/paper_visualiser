# Copy-paste prompt (use when the skill isn't installed)

Make a 3Blue1Brown-style explainer video of the attached paper, about 3–4 minutes:
Manim for visuals, Kokoro TTS (voice af_heart, speed ~1.08) for narration, 1080p60.

Process — follow it strictly:
1. Read the whole paper. Pick 3–5 key ideas. Arc: hook (concrete image + question) → title card
   → one scene per idea → real-data results → most surprising result → recap. For each idea name
   ONE signature visual transformation that embodies it. Give each recurring concept one colour
   for the whole video.
2. Write the narration FIRST as scenes → beats (one idea / one visual change per beat, 4–14 s).
   Budget ~150 words per minute (≈520 words for 3.5 min); count and cut before generating.
   Write for the ear: spell out acronyms and numbers ("H R eighty-seven ninety-nine", "C O",
   "Earth masses"), one number per sentence, no symbols or parentheses.
3. Generate one TTS clip per beat; concatenate per scene with 0.5 s lead, 0.4 s gaps, 0.9 s tail;
   save each beat's start time to JSON. Adjust TEXT (not speed) until the total fits.
4. Each Manim scene: add the scene's audio at t=0, call `beat(k)` = wait until beat k's start
   time before animating what that sentence says; warn when a beat's animations overrun; end by
   waiting for the audio and fading out. Fix every overrun.
5. Style: near-black background, small fixed palette, LaTeX text (Tex/MathTex) for the 3b1b look,
   numbered section headers, real equations and numbers from the paper. Use 3b1b moves:
   transform one representation into another, ValueTracker sweeps with live readouts, equations
   that grow terms (TransformMatchingTex), zoom by swapping axes, thresholds with red excess,
   counting numbers, a recap flow chart.
6. Render drafts at low quality, scenes in parallel, each with its own --media_dir (shared LaTeX
   cache races). Make contact sheets (ffmpeg tile, a frame every 3 s) and LOOK at every one:
   fix overlaps, labels on data, off-frame items, curves leaving axes, tiny text, empty space.
   Iterate 2–3 times.
7. Render 1080p60, concatenate, mix a very quiet music bed, loudness-normalise to −16 LUFS.
   Deliver the final MP4 plus a voice-only version, and list simplifications, recomputed numbers,
   and that pronunciation wasn't checked by ear.
Environment: use a Python 3.12 venv for Kokoro (spaCy deps fail on 3.13); needs LaTeX + dvisvgm,
ffmpeg, pango, espeak-ng.
