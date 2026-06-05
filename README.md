# Random

A collection of small projects and experiments, built as a static site with [Zola](https://www.getzola.org/) and deployed to GitHub Pages.

## Projects

### 🎯 Spot It!
A real-time multiplayer card game based on Spot It / Dobble.

- One player creates a room and shares the 6-character code with friends
- Each player gets a circular card with 8 emoji symbols
- Any two cards in the deck share **exactly one** symbol — find it first to score
- No backend needed: players connect directly via WebRTC (PeerJS)

Live at: `https://juanandhisbot.github.io/random/spotit/`

### 📚 Français de Base
A beginner French study guide for Spanish speakers.

Live at: `https://juanandhisbot.github.io/random/`

---

## Local development

### With Docker (recommended)

```bash
docker compose up
```

The site is served at <http://localhost:1111> with live reload on file changes.

### Without Docker

Install [Zola v0.19.2](https://www.getzola.org/documentation/getting-started/installation/), then:

```bash
zola serve
```

---

## Project structure

```
.
├── config.toml        # Zola site config
├── content/           # Markdown pages
├── templates/         # Tera HTML templates
├── static/            # Static files (CSS, JS, standalone pages)
│   └── spotit/
│       └── index.html # Spot It game (self-contained)
└── public/            # Build output (git-ignored)
```

## Deployment

Pushes to `main` automatically build and deploy via GitHub Actions.
