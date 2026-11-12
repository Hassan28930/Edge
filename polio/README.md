# Polio is back. But why?

A self-contained, **67-second, 9:16 code-drawn animated film** in the attached *Inside Out* style. The repository's existing new-tab pages are untouched; this project lives entirely in `polio/`.

- **Picture:** 1080 × 1920, 30 fps, 30 short shots. Pure Canvas 2D vector shapes; deterministic rendering from any timestamp. No stock imagery, gradients, gore, or external runtime requests.
- **Audio:** selected Hindi/Hinglish educational voice, a quiet original synthesized music bed, and subtle procedural edit effects.
- **Captions:** authored **English translations**, timed in short 1–3 word chunks with one yellow emphasis word. Since the voice is Hinglish, caption cue times are authored rather than naïvely matched by spelling.
- **Deliverable:** `export/polio-is-back-vertical.mp4` (H.264/AAC, exactly 67.00 s). The MP4 is intentionally ignored by Git but is present in this workspace; render it again from source with the command below.

## Run and render

```sh
cd polio
npm install
npm run dev             # preview at http://localhost:4173
npm run check           # storyboard, timing, caption, and audio assertions
npm run audio           # remake audio/mix.m4a from the seven supplied voice clips
npm run render          # export/polio-is-back-vertical.mp4, 1080x1920 @ 30 fps
```

More render options:

```sh
npm run render:draft                                  # 540x960 @ 15 fps
npm run render -- --still=24.9 --output=export/24.png # a full-size frame
npm run render -- --sheet                             # one 540x960 still per shot
npm run render -- --draft --from=20 --to=26           # short review render
```

The export tool runs Chromium from the npm package, streams PNG frames directly to the npm-packaged FFmpeg binary, and muxes the provided narration mix. The included render tool targets Linux x64 (the preview itself is ordinary browser JavaScript). No system Chrome or FFmpeg install is needed. The player uses relative URLs, has chapter seeking, play/pause, mute, and caption controls, and shows an MP4 download link after rendering.

## Edit map

| File | Purpose |
| --- | --- |
| `script.json` | 67-second timeline, chapter starts, voice placement, shot order, English caption cues |
| `narration.md` | Original Roman-script brief and the spoken Devanagari transcription |
| `src/shots.js` | The 30 per-shot visual compositions, all pure functions of time |
| `src/core/kit.js` | Reusable flat-vector hero, x-ray body, child, virus, vial, shield, clinic, clock, calendar, globe |
| `src/core/lib.js` | Palette, logical frame size, easing and drawing primitives |
| `src/core/captions.js` | Word highlighting, auto-fitting, 0.2 s pop, caption safe area |
| `src/main.js` | Camera push, cut flashes, timeline player, exact-frame renderer API |
| `tools/prepare-audio.mjs` | Mix the voice clips, original quiet bed and procedural sound cues |
| `tools/render.mjs` | Headless frame capture and MP4 encode; also stills and contact-sheet frames |
| `tools/server.mjs` | Minimal static server with audio/video byte-range support |

**Visual grammar:** cream `#F4F1EA`, skin `#E8B89A`, organ pink `#E57A8A`, danger red `#D62839`, x-ray-only cyan `#4FD1E8`, highlighted yellow `#FFD43B`, ink `#1A1A1E`. Red signals a problem; x-ray changes the entire body except the normal head. The final image and the call to reach every child close the loop to the opening question.

**Editorial note:** The figures and wording come from the supplied script. Before public distribution, verify time-sensitive statistics (including vaccine dose totals and saved lives) against current WHO/GPEI reporting. Vaccine-derived outbreaks occur where immunity is low; the newer vaccine is *less likely* to revert, not incapable of doing so. This is an explainer, not medical advice.
