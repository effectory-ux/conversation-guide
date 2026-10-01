# Conversation Guide

The Conversation Guide prototype: the guide that helps a manager bring their
team's results to the team before deciding what to do, and the document they
download from it.

Moved here from `effectory-design/effectory-design-documentation` on 2026-09-16.

## Prototypes

| File | What it is |
|---|---|
| `conversation-guide-v1.html` | **Version 1**: a full width band between At first glance and What needs focus, so the guide is offered before the focus areas |
| `conversation-guide-v2.html` | **Version 2**: a card inside the focus stack, after the three focus areas and the areas Explore more opens, at the cards' own width |
| `conversation-guide-v3.html` | **Version 3**: a popup from the bottom right, two seconds after landing |
| `conversation-guide-v4.html` | **Version 4** (*birch*): the next version after the usability test. Flow A in Figma. See below |

The three differ only in **where** the guide is offered. Every route into it, the
card, the Actions page and the success screen alike, opens the guide itself in a
dialog with a zoom control and *Download a copy*, so a difference between the
versions is a difference in placement and nothing else.

There is no side panel: it described the guide instead of showing it, and once
the dialog could show the real thing there was nothing left for it to do.

## Version 4, after the usability test

Versions 1 to 3 (tags *oak*, *river*, *pine*) were tested with 11 managers on
UserTesting, 24 to 28 Sep 2026. Oak, version 1, was ranked first by 7 of 11 and was
the only one nobody failed to find again. Version 4 builds on it and matches
**Flow A · Conversation guide v02** in the Figma Conversation Guide file:

- **Same place as oak**, right under At first glance, but its own block on the info
  tint, so it cannot pass for a focus card (river's problem).
- **The button reads as a button**: a book icon, a *Download PDF* action beside it and
  a line saying where else the guide lives. One participant read oak's small teal
  button as information, like the teal chips in the matrix above it.
- **Reading first, download second**: the dialog keeps the guide in the page; *Download
  a copy* is the footer link.
- **Show your team**: a second tab with a page to put on screen, with the focus areas,
  wins and today's plan but no facilitator notes, and *Present full screen*.
- **The card stays**: after *Done* it is where it was and says when it was opened.
- **Collapsing shrinks it to one line** in the same place: the card's chevron up
  collapses it, the line's chevron down expands it again, and *View the guide* stays on
  the line. It lasts across reloads and visits (localStorage), so add `?reset` to the URL
  to start a session fresh.
- **No popup**, and no *Do not show this again*.

`ac-overview-embed.html` is the Overview fragment both load in an iframe; it is
not a prototype on its own.

`guide/` holds the conversation guide document: the PDF the side panel's
**Download guide** button hands over, and the original content it came from.
See `guide/README.md`.

## Where the Action Center prototypes went

They used to live here too. They now have their own repo,
[effectory-ux/action-center](https://github.com/effectory-ux/action-center),
published at <https://effectory-ux.github.io/action-center/>, so the copies here
were removed on 2026-09-18 rather than left to drift. The prototype toolbar and
its `proto-config-ac.js` went with them: nothing here loaded them.

The Conversation Guide builds on the stepper version of that prototype, so when
its Focus view or Actions page changes, the change usually belongs here too.

## Building blocks

`tokens.css`, `foundation.css`, `components.css`, `icons.js` and `assets/` are
copies from the Engage design system, kept here so the prototypes render without
a build step. `effectiveness.css`, `effectiveness.js` and `i18n.js` belong to the
Overview embed, and `assets/illustrations/win-small.svg` and `improve-small.svg`
are loaded by `effectiveness.js`.

## Running locally

Serve the folder over HTTP — the prototypes load assets by root-relative path, so
opening a file with `file://` will not work.

```
python3 -m http.server 8000
```

Then open <http://localhost:8000/conversation-guide-v1.html>.
