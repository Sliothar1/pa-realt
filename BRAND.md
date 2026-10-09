# The PA family brand

PA is the shared brand for Garry Lohan's open-science sites: **PA Marine** (Irish coastal biotoxin early warning) and **PA Réalt** (Irish monuments and the sky), with room for more. Each site has its own colour, but they share one structure and one type system, so they read as sister sites.

## Shared structure (every PA site)

1. **Hero `.hero`** contains:
   - **`.topline`**: the PA mark plus the site name (`.brandlink`), a few top links (`.toplinks`; links marked `.opt` drop out on mobile), and a ◐ theme toggle.
   - **`.headline`**: the site's line-art **emblem** (inline SVG, single-weight stroke), the eyebrow **"Fáilte · Welcome"**, an `h1` in the serif face, and a one-line `.sub`.
2. **Sections `.sect`**, each with an **Irish label in italic serif** (`.ga`) above the English title, e.g. *Tástálacha* / Pre-registered tests, or *Foinsí agus ceadúnais* / Data, sources & licences. Irish appears as a companion, never as decoration-only text, and every Irish string is sourced (focloir.ie, Tailte Éireann/logainm, Fingal bilingual leaflet). If no sourced term exists, leave it blank.
3. **Credit section "Fúinn · About"**: "a project by Garry Lohan (… ATU Galway)", with an honest scope and disclaimer paragraph.
4. **PA family strip `#paFamily`**: a small row with one chip per sister site (mark + name). The current site is shown as "you are here". It is generated from `PA_CONFIG.family` in `site/js/config.js`, so adding a site means adding one line.
5. **Footer**: a **seanfhocal** with its translation, then "Déanta i nGaillimh · Made in Galway", the © line and data credits.
6. **Fixed bottom demo strip `.disclaimer`**: one short line stating that this is a research prototype and not an official product.

## Shared type system

- **Body and UI:** system sans (`system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`).
- **Display, h1/h2 and Irish labels:** `"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif`, with the Irish labels in italic.
- No web-font downloads: it's fast, private and works offline.
- **Scale:** h1 `clamp(2.2rem, 5vw, 3.6rem)`; section titles ~1.6–2rem; body 16–17px, line-height 1.6.
- Numbers use tabular figures in tables.

## Marks and emblems

- **PA mark** (`#i-pa`): a small rounded square with "PA" set in the serif. It is the same on every site; only the colour comes from the site palette.
- **Site emblem.** Each site gets one single-stroke line-art icon:
  - PA Marine: a **dolphin**.
  - PA Réalt: a **passage-tomb mound with the roof-box slot, a gold beam to the rising Sun, and one twinkling star**.
- **Emblem rules:** stroke 1.5–2 px with round caps, no fills except a small accent, and it must read at 24 px.
- **Ornament** (PA Réalt): original spiral, triple-spiral and lozenge line art inspired by passage-tomb art. These are not traced copies of specific stones.

## Palettes

| Role | PA Marine | PA Réalt |
|---|---|---|
| Background | navy `#061f33` | maroon-black `#140a0d` to midnight `#0e0f1e` |
| Panel | deep sea `#0b2c45` | oxblood/maroon `#2a0f16`, raised `#3a141d` |
| Accent / buttons | sea-glass `#8fe0d6` | maroon `#6e1a28` with a gold `#e8b860` outline/text |
| Light / data highlight | sea-glass | soft warm gold `#f3d79b` (rays, beams), deep gold `#b98a35` (lines) |
| Text | pale foam | cream `#f7ecd6`, secondary `#e6d3b3`, muted `#b89c82` |
| Moon / cool note | | moonlight lilac `#ddd6e8` (used sparingly) |

**PA Réalt mood.** It should feel luxurious, confident and warm: deep maroon and oxblood with rich gold over a night background. The intent is secure, friendly and approachable, the feeling of a winter fire and the first gold light in the passage. It should not feel cold or mysterious; the aim is to make people love the stars and the people who built for them.

- Gold is reserved for light: rays, the beam, star highlights and links.
- Panels and buttons are maroon.
- Text is always cream on dark, with contrast ≥ 7:1 for body text.
- A lighter **dawn** theme (◐) swaps to parchment and maroon ink while keeping the same roles.

## Naming and configuration

- The site name, Irish name, subtitle, credit and family links live in **one place**: `site/js/config.js` (`window.PA_CONFIG`).
- `scripts/stamp.py` writes the name into the static `<title>` and meta tags, so the name is still correct without JavaScript.
- To rename: edit `config.js`, run `python scripts/stamp.py`, and commit.

The name follows the pattern **"PA <Irish word>"** where it fits:
- *Réalt* means "star" (focloir.ie: réalta/réalt, star).
- The subtitle gives the English sense: "Stone and Sky" (*Cloch agus spéir*).

## Voice

- Plain, warm and exact.
- Cite everything, and say "claim", "observed" or "tested" precisely.
- Show the honest result even when it is "not supported".
- Irish touches are welcoming, not nationalistic.
