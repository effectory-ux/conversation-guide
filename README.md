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
| `conversation-guide-v3.html` | **Version 3**: the same band as version 1, but the card opens the guide itself in a dialog rather than the side panel that describes it |
| `conversation-guide-v4.html` | **Version 4**: a popup from the bottom right, two seconds after landing |

Versions 1, 2 and 4 differ only in **where** the guide is offered; the card copy
and call to action are the same in all three, so a difference between them is a
difference in placement.

Version 3 changes **what the card opens**, not where it sits: it shares version
1's placement so the two can be compared directly. Its call to action reads *View
guide* rather than *See details*, because it delivers the guide rather than an
explanation of it, and the dialog carries *Download a copy* for anyone who wants
the file.

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
