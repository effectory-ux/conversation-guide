# Conversation Guide

The Action Center · Manager and Conversation Guide prototypes: the pages a
manager sees after a survey, and the guide that helps them bring the results to
their team before deciding what to do.

Moved here from `effectory-design/effectory-design-documentation` on 2026-09-16.

## Prototypes

| File | What it is |
|---|---|
| `conversation-guide-v1.html` | Conversation Guide, **version 1**: the entry card sits in the page, above the focus cards |
| `conversation-guide-v2.html` | Conversation Guide, **version 2**: a popup appears from the bottom right two seconds after landing |
| `action-center-manager-stepper.html` | Action Center · Manager, stepper version (the one the guide builds on) |
| `action-center-manager.html` | Action Center · Manager |
| `action-center-manager-v4.html` | Action Center · Manager, v4 |
| `action-center-manager-v5.html` | Action Center · Manager, v5 |

v1 and v2 are the A/B pair for user testing: same title and description, one
entry point each, no variant switcher.

`ac-overview-embed.html` is the Overview fragment the prototypes load in an
iframe; it is not a prototype on its own.

`guide/` holds the conversation guide document itself: the PDF the side panel's
**Download guide** button hands over, its design source and the original content.
See `guide/README.md`.

## Building blocks

`tokens.css`, `foundation.css`, `components.css`, `icons.js` and `assets/` are
copies from the Engage design system, kept here so the prototypes render without
a build step. `effectiveness.css`, `effectiveness.js` and `i18n.js` belong to the
Overview embed. `toolbar/` is the shared prototype toolbar (a copy of
`effectory-ux/prototype-toolbar`); `proto-config-ac.js` is what the Action Center
prototypes put in it.

## Running locally

Serve the folder over HTTP — the prototypes load assets by root-relative path, so
opening a file with `file://` will not work.

```
python3 -m http.server 8000
```

Then open <http://localhost:8000/conversation-guide-v1.html>.
