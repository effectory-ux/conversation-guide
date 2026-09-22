# Conversation Guide

The Conversation Guide prototype: the guide that helps a manager bring their
team's results to the team before deciding what to do, and the document they
download from it.

Moved here from `effectory-design/effectory-design-documentation` on 2026-09-16.

## Prototypes

| File | What it is |
|---|---|
| `conversation-guide-v1.html` | **Version 1**: a full width band between At first glance and What needs focus, so the guide is offered before the focus areas |
| `conversation-guide-v2.html` | **Version 2**: a full width row at the foot of What needs focus, under the cards and the heading beside them |
| `conversation-guide-v3.html` | **Version 3**: a popup from the bottom right, two seconds after landing |

The three are the set for user testing: same title, description and call to
action, one entry point each, no variant switcher. Everything else about them is
identical, so a difference in the results is a difference in placement.

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
