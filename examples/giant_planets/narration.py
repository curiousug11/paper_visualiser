# Narration, split into scenes and beats. Each beat is one TTS clip; Manim
# scenes sync their animations to beat start times.
SCENES = {
    "s0_hook": [
        "Every giant planet carries a record of its birth, written in the gases of its atmosphere.",
        "Telescopes can now read that record: how enriched a planet is in carbon, oxygen, nitrogen, even sulfur, compared to its star.",
        "But five times stellar oxygen isn't a story yet. How much rock and ice did the planet swallow? And where did it come from?",
        "A new paper by Chachan, Murray-Clay, and Fortney builds the dictionary between the two.",
    ],
    "s1_mass": [
        "Step one: turn enrichment into mass. Abundances are measured relative to hydrogen, then compared to the star. Call that ratio, x.",
        "But elements don't count equally. In the Sun, oxygen carries about forty-two percent of the heavy-element mass, and carbon another eighteen.",
        "So we take a weighted average: each element's enrichment, weighted by its share of the star's metal mass. Call it, x bar.",
        "Then the planet's metal mass fraction is one compact formula. For a Sun-like star, it's just x bar, over seventy plus x bar.",
        "Ten times solar in everything gives about twelve percent metals. Ten times solar in oxygen alone, only six.",
        "For the planet H R eighty-seven ninety-nine b, x bar is near five. About six and a half percent of its mass is metal.",
    ],
    "s2_split": [
        "Step two: separate what arrived as solids from what arrived as gas.",
        "Elements like sulfur, iron, and silicon live almost entirely in rock, so only solids can deliver them. Their enrichment directly measures how much solid the planet ate, per unit of hydrogen.",
        "Volatiles, like oxygen, are split. A fraction f is frozen into solids, the rest is gas, depending on which snowlines the planet sits beyond.",
        "That gives a simple bookkeeping rule. The solid share scales with the refractory enrichment. The gas share stays fixed, because gas brings its own hydrogen.",
        "Here's the payoff. A static disk puts a ceiling on volatile enrichment. Blow past it, and the disk must have moved volatiles around. For example, pebbles drifting inward and evaporating, enriching the gas.",
        "That excess becomes a measurable quantity.",
    ],
    "s3_apps": [
        "Now, real planets. For A F Lep b, about nine A U from its star, the simple static disk works. Three quarters of its oxygen, and half its carbon, came in solids.",
        "That's about fifty-six Earth masses of metals, mostly from solids. Far more than classic models let a growing core grab.",
        "H R eighty-seven ninety-nine has four giant planets. For the inner three, a static disk fails. It would need more than all their carbon and oxygen in solids.",
        "But add gas enriched in carbon monoxide, about three times solar, and one value fits all three. The outermost planet, between the C O and nitrogen snowlines, points to nitrogen-rich gas instead.",
        "And those inferred birthplaces match where the planets are today. No large migration needed.",
    ],
    "s4_disk": [
        "That excess carbon monoxide leads to a striking result: a new way to weigh the disk.",
        "The extra C O came from ice, sublimating off pebbles as they drifted across the C O snowline. But each pebble loses only about seventeen percent of its mass there.",
        "The inner planets took in about a hundred twenty-eight Earth masses of excess C O. Divide by seventeen percent: at least seven hundred fifty Earth masses of pebbles streamed past.",
        "Nearly double the metal in all four planets combined.",
    ],
    "s5_outro": [
        "So, the recipe. Measure carbon, oxygen, and one refractory. Convert enrichment to mass. Split solids from gas. And read the disk's history in what's left over.",
        "As telescopes survey whole populations of giant planets, tools like this, released as open source code, turn spectra into histories of how worlds are made.",
    ],
}
