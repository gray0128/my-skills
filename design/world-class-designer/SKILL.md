---
name: world-class-designer
description: Design and polish distinctive, studio-quality UI, web pages, and interactive prototypes without generic AI slop. Use when the user asks to design or redesign a landing page, app interface, UI component, visual prototype, or frontend experience, or explicitly invokes world-class-designer.
---
# World-Class Designer

Guide AI coding and design agents through an AI-native Double Diamond workflow (Discover, Define, Deliver) to break out of predictable next-token defaults and ship distinctive, high-taste interfaces.

## When to Use

- Designing a new landing page, web app, mobile interface, or interactive prototype from scratch
- Redesigning or polishing an existing UI that looks like generic AI slop (purple gradients, cookie-cutter split layouts, excessive cards, or glowing borders)
- Orchestrating coding agents, visual critic subagents, and media generation tools to build high-craft frontend experiences
- Responding to explicit requests for `world-class-designer` or studio-grade UI/UX design

## Steps

1. **Discover: Inject External Entropy and Co-Steer Bold Briefs**

   - Never rely on vague prompts like "make it unique, modern, or random", which still converge on modal training patterns.
   - **Technique 1 (String Seed of Thought)**: When open-ended divergence is needed, run a shell command to generate a random alphanumeric string, derive the color palette, typography, grid proportions, and visual metaphors from subpatterns in that string, and build the concept without exposing the seed string in the UI.
   - **Technique 2 (Three-Step Ambitious Brief)**: When exploring directions with the user:
     1. Pitch 5-8 distinct, high-level aesthetic archetypes (one sentence each, such as tactile industrial control panel, editorial print monograph, or isometric living city).
     2. Ask the user which direction resonates and what specific textures, interactions, or anti-patterns they want to keep or avoid.
     3. Distill the chosen direction into a concrete, opinionated build prompt before writing UI code.

2. **Define: Deepen Identity with Blind Visual Critics and Rich Media**

   - **Technique 3 (Fresh-Context Visual Critic Loop)**: Do not judge visual quality from code alone. After rendering the UI:
     1. Capture a screenshot of the live interface.
     2. Evaluate the screenshot in a fresh context (without implementation code or prior rationale) against a top design studio baseline, or rank it alongside 3-4 reference studio screenshots.
     3. Penalize obvious AI giveaways, list specific structural and detail gaps, and score out of 10.
     4. Run 1-2 focused refinement iterations until the score reaches 9/10 or converges.
   - **Technique 4 (Bespoke Visual Assets over CSS Placeholders)**: Replace code-drawn gradients, generic SVG blobs, and empty colored boxes with generated or curated imagery, custom shaders, or 3D assets. Keep any development API keys in a gitignored `.env.agents` file, never hardcoded in source.
   - **Technique 5 (Motion and Keyframe State Transitions)**: When motion adds narrative value, use looping background-matted video clips for complex physical/refraction effects, or generate keyframe-interpolated transition clips between product states and bind frame scrubbing to scroll or gesture input.

3. **Deliver: Subtractive Polish, De-Slop, and Human-Grade Copy**

   - **Technique 6 (Ruthless Subtraction)**: Audit every element on screen and remove anything that does not add information, functionality, or state feedback. Delete gratuitous background glows, gradient progress bars, random colored text highlights, redundant container cards, and secondary labels where visuals already communicate meaning. Prefer clean platform-native controls over clunky custom inputs.
   - **Technique 7 (Strip AI Tells)**: Eliminate stereotypical AI layout and styling habits, including default purple/indigo neon palettes, symmetrical 3-column icon cards, decorative emojis in headings, and fake dashboard chrome.
   - **Technique 8 (Tighten High-Leverage Copy)**: Replace generic, repetitive AI marketing filler with sharp, concrete copy across headlines, primary CTAs, empty states, and error messages, or flag those exact strings for the user's personal voice pass.

## Gotchas

- Do not let a coding agent grade its own UI without inspecting a rendered screenshot; code-level self-review almost always rationalizes mediocre visual hierarchy.
- Do not embed the target passing score (such as "give this at least 9/10") inside the critic prompt; keep the critic rubric objective and enforce the stopping threshold in the outer loop with a hard cap of 2-3 iterations to prevent runaway token burn.
- Remember that LLMs naturally add elements to solve problems; during the Deliver phase, prioritize deleting unnecessary wrappers, labels, and decorative effects so layout and negative space carry the hierarchy.
