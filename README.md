# Source Academy Documentation

> Centralised documentation for Source Academy, built with [VitePress](https://vitepress.dev/).

## Quick Start

Needs Node 24 (the version in `.node-version`; see the [Node.js version](app/developer/node-version.md) page).

```bash
# Install dependencies
yarn

# Start dev server
yarn dev

# Build for production
yarn build

# Preview production build
yarn preview
```

## Documentation

The site is published at <https://docs.sourceacademy.org> in three sections, like the [about site](https://about.sourceacademy.org/): [developer](https://docs.sourceacademy.org/developer/), [educator](https://docs.sourceacademy.org/educator/) and [learner](https://docs.sourceacademy.org/learner/). It is built from this repository by `.github/workflows/deploy.yml` on every push to `main`, into the deployment repository [`docs.sourceacademy.org`](https://github.com/source-academy/docs.sourceacademy.org), next to the language documentation (`/javascript`, `/python`).

The pages are the Markdown files under `app/`: `app/developer/` is `/developer/`, and so on. For the tool that builds them:

- [VitePress Documentation](https://vitepress.dev/) - Official VitePress docs
- [Default Theme Config](https://vitepress.dev/reference/default-theme-config) - Theme configuration reference

## Links

A link checker ([lychee](https://github.com/lycheeverse/lychee), configured in `lychee.toml`) runs on every pull request, and every Monday, over the built site and this README (`.github/workflows/links.yml`). A run that finds a dead link fails; the sites that refuse automated clients (403 and 429) are not counted as dead. The READMEs of the organisation's other repositories are checked by the monthly scan (`tools/org-health`).

## Scripts

| Command           | Description                  |
| ----------------- | ---------------------------- |
| `yarn dev`        | Start development server     |
| `yarn build`      | Build for production         |
| `yarn preview`    | Preview production build     |
| `yarn format`     | Format code with Prettier    |
| `yarn lint:spell` | Spell check docs with cspell |
