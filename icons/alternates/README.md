# Alternate icon directions

Not wired into the app. Kept because they may be worth revisiting.

## `notebook.svg`

A notebook with binder rings, note lines and a checkmark badge, on a dark card
with gradients and a drop shadow.

Reads well at 512px. Two reasons it isn't the shipped mark:

- **It doesn't survive shrinking.** Binder rings, four note lines and a badged
  checkmark are roughly a dozen elements inside 512 units. At 16px — the size a
  favicon is actually used at — they collapse into noise. The shipped tally was
  designed the other way round: legible at 16px first, scaled up from there.
- **The metaphor is crowded.** Notebook-plus-checkmark is the icon most
  productivity tools already use. A tally says "counting things as they happen",
  which is narrower and more specific to what this app does.

The PNGs generated from this SVG (`icon-192.png`, `icon-512.png` at the repo
root) were blank — a single flat `#e0714a` across every pixel, no artwork. The
rasterizer silently produced a filled square. They were removed rather than
regenerated. If this direction is ever revived, render it with something that
handles gradients and filters, and **look at the output** before committing it.
