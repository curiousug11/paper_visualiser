# Narration: one entry per scene, one string per BEAT (a beat = one idea = one visual change).
# tts.py turns each beat into a clip and records its start time; scenes call self.beat(k)
# to start beat k's animations exactly when its sentence starts.
#
# Budget: ~150 spoken words/min at speed 1.08 incl. gaps. 3.5 min ~ 520 words. Beats of 5-14 s.
# Write for the EAR: spell out what TTS mangles ("H R eighty-seven ninety-nine", "C O", "A U",
# "Earth masses", "x bar"), short sentences, one number per sentence, no parentheses.
SCENES = {
    "s0_hook": [
        "Replace me: a concrete image or question that makes the viewer care.",
        "Replace me: name the paper and promise what the viewer will understand by the end.",
    ],
    "s1_idea": [
        "Replace me: step one, the first key idea.",
        "Replace me: the payoff of step one, with one real number from the paper.",
    ],
}
