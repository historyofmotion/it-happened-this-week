# It Happened This Week — Product & Technical Specification

**Version:** 0.8 (draft)
**Date:** 2026-07-25
**Owner:** David
**License:** Apache-2.0 — see [LICENSE](./LICENSE)

**Changes from 0.7:** the AI narrative is now a **real call to the Anthropic Messages API** — request shape, prompt, failure paths and the browser-key security position are all specified (§5.3.1).

**Changes from 0.6:** notes may be **multi-line** (§4.4.1). The capture field is an auto-growing textarea; `Enter` still saves, `Shift+Enter` inserts a line break.

**Changes from 0.5:** Capture gains a **per-project note count** on each tile and a **per-project note list** beneath the controls, where editing and deleting now live (§4.5). Summarize becomes read-mostly — **no deleting there at all** (§5.2). The Past weeks settings tab is gone; `←` `→` and *This week* already covered it.

**Changes from 0.4:** a note's week is now **derived from its timestamp, never stored** (§8.1) — the previous design would have mis-filed notes after the app sat unopened over a weekend. Storage status is surfaced in the header, and Disconnect / Reconnect are specified (§6.3).

**Changes from 0.3:** named — *It Happened This Week*. Settings is fully editable, and §7 now specifies each control, what it changes, and when it takes effect.

**Changes from 0.2:** in-app Capture is now click-first — all projects are visible as tiles with number shortcuts, replacing the single chip and `#` picker. Pasted URLs attach themselves with no button press. The keyboard-first, chrome-minimal capture design moves to a separate Chrome extension widget (§4.8).

**Changes from 0.1:** restructured around two modes (Capture / Summarize) with everything else demoted to management; links are a first-class part of a note; file-backed storage with create/open/import/export, all confined to a Settings dialog; explicit return-to-current-week.

---

## 1. Summary

A single-user web app for capturing work accomplishments as they happen, organized by project, and rolling them up into a weekly status report. The core bet is that status reports fail because logging is expensive at the moment of accomplishment and impossible to reconstruct on Friday. So the capture path must be near-zero friction: open, type or speak one line, done.

---

## 2. Goals

| # | Goal | Success measure |
|---|------|-----------------|
| G1 | Capture a note in under 5 seconds from anywhere | Keystroke-to-saved ≤ 5s, ≤ 3 interactions |
| G2 | Never lose data; work offline | 100% of notes persist without network; a durable copy exists outside the browser |
| G3 | Produce a shareable weekly summary in one click | Copy-to-clipboard output ready to paste into email/Slack |
| G4 | Preserve history | Any past week retrievable and readable, with one click back to now |

### Non-goals (v1)

- Multi-user, teams, shared projects, permissions
- Task/project management (due dates, assignees, status tracking)
- Integrations (Jira, GitHub, Slack, calendar)
- Mobile-native app
- Accounts or a hosted backend

---

## 3. Information architecture

The app has exactly **two modes** in the primary UI. Everything else is management, reached from a settings/utility surface and never in the main path.

```
┌──────────────────────────────────────────────┐
│  [ Capture ]  [ Summarize ]           ⚙︎      │
└──────────────────────────────────────────────┘

MODE 1 — CAPTURE          MODE 2 — SUMMARIZE        MANAGEMENT (⚙︎)
add notes & links         review + generate         projects
project tiles + counts    week selector             storage / file
always "now"              ← → and “This week”       import / export
no week navigation        list + AI narrative       AI key
edit / delete notes       copy out                  shortcuts, theme
                          read-mostly
```

**Writes belong to Capture, reads belong to Summarize.** Creating, editing and deleting a note all happen in Capture, beside the note in question. Summarize shows the week and produces the output; the only thing it mutates is the highlight flag. Keeping destructive actions out of the review surface means you can scan the week without a delete button under your cursor.

A third capture surface — the keyboard-first **Chrome widget** — is planned for v2 (§4.8). It is a capture surface only and does not change this structure.

### 3.1 Why Capture has no week navigation

Capture always writes to *now*. There is no week selector, no date picker, no way to be in the wrong week. This removes an entire class of error and keeps the mode to a single decision (which project) with a good default. Backdating is possible but lives in Summarize, where you're already looking at a specific week.

### 3.2 Mode switching

- `Cmd/Ctrl+Shift+Tab` toggles modes. Plain `Tab` is reserved for focus traversal across the project tiles.
- The mode toggle is the only persistent chrome besides the settings gear.
- App always launches into **Capture**, cursor in the field. Launching the app is the capture action.

---

## 4. Mode 1 — Capture

The in-app capture surface is **click-first**. Everything you need is visible; nothing is hidden behind a keystroke you have to remember. The keyboard-first design — one chip, a `#` picker, no visible project list — is a genuinely different interaction model and lives in the Chrome widget (§4.8), not here.

### 4.1 Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ ● Atlas Migration ③⌥1  ○ Q3 Hiring ②⌥2  ○ Docs ⓪⌥3   [+ New]  │  ← count = notes this week
├──────────────────────────────────────────────────────────────────┤
│ Cut over the staging cluster                                     │
│ Zero downtime; rollback rehearsed twice          ⏎ grows [🎙][Save]│
│ ⛓ github.com/acme/atlas · PR #882                             ×  │  ← appears on paste
└──────────────────────────────────────────────────────────────────┘

Atlas Migration · this week · 3
  Traced the connection-pool leak to the retry wrapper        Thu  ×
  ★ Cut over the staging cluster                              Mon  ×
    Zero downtime; rollback rehearsed twice
    ⛓ runbook
```

- **Project row** — every active project as a tile, always visible, each carrying its **note count for the current week** (§4.2.1). The selected tile is filled and outlined in the accent color. Wraps; no scroll, no dropdown, no search.
- **Capture field** — auto-focused on load, full width, one row tall and growing with the note (§4.4.1).
- **Project note list** — the notes already logged this week *for the selected project*, newest first (§4.5). This is where editing and deleting happen.
- Nothing else. No stats, no charts, no week rollup — that's Summarize's job.

### 4.2 Project selection

- **Click any tile.** One click, no menu, no typing. This is the primary path.
- **Number shortcuts** select project *n* — see §4.3 for which modifier, because the obvious choice has a conflict.
- **Last-used project stays selected** across saves and sessions, so consecutive notes about the same thing need no project interaction at all.
- **`+ New`** opens an inline name field; the project is created and selected in one step.
- Tiles are ordered by the user's `sortOrder` (set in Settings), *not* by recency — a tile that moves is a tile you have to re-find, and it breaks the number shortcuts' muscle memory.
- Above ~10 active projects the row gets unwieldy; that's the signal to archive some. Settings shows a gentle note when a project has had no notes in 60 days.

#### 4.2.1 The count badge — the point is the zeros

Each tile carries the number of notes logged against that project **in the current week**. It answers the question you actually have on Thursday afternoon: *which of these have I not written anything about?*

- A non-zero count is quiet — filled pill, muted text. It's reassurance, not information you need to act on.
- **Zero is styled differently** — dashed outline in the warning color. It's the only actionable state, so it's the only one that draws the eye. Four projects showing `3 2 4 0` should make the `0` the thing you see first.
- The count is derived, never stored, and updates on every save, delete, and week change.
- It counts the *current* week only, regardless of what Summarize is looking at — Capture has no concept of other weeks (§3.1).

This is deliberately a count and not a staleness indicator ("4 days since last note"). A count is unambiguous and needs no interpretation; the zero carries all the signal that matters.

### 4.3 Number shortcuts — the modifier conflict

`Cmd+1…9` is what you'd want, but **browsers reserve it for tab switching and a web page cannot intercept it.** In a normal Chrome/Safari tab, `Cmd+2` will switch tabs no matter what the page does. Three answers, and the spec uses all three:

1. **`Alt/Option+1…9` — the default, works everywhere.** Interceptable in every browser, no conflict with anything the browser or OS claims. Tiles display `⌥1`, `⌥2`, ….
2. **`Cmd/Ctrl+1…9` — enabled automatically when running as an installed PWA.** A standalone PWA window has no tab strip, so the browser releases the binding. The app detects `display-mode: standalone` and relabels the tiles to `⌘1`, `⌘2`, …. This is one more reason to install it.
3. **Bare `1…9` when the capture field is empty.** Zero-modifier and fast; the moment you've typed anything, digits type normally. Free to support, costs nothing, and is what a keyboard user reaches for first.

The tile label always shows the binding that's actually live in the current context, so it's never a guess.

### 4.4 Notes and links

A note is a short block of text — one line or several (§4.4.1) — optionally with **one attached link**. There is **no link button**: paste is the entire interface.

- **Paste a URL with other text** → the URL is lifted out of the body, attached as a chip below the field, and the surrounding text you typed is preserved intact.
- **Paste a bare URL alone** → attached as a link-only note; the chip shows the domain and a shortened path. Type a body afterward if you want one, or just hit Save.
- **Type a URL** (not just paste) → same detection, fired on input.
- **Chip behavior:** click the chip's text to type a custom label inline; `×` removes it and returns the URL to the body text so nothing is lost by accident.
- The app **fetches nothing** — no title lookup, no favicon, no preview. It's offline-first and a network call here would be the only thing standing between you and a saved note.
- Links render as a chip under the note in Summarize and as inline Markdown (`[label](url)`) in the exported summary.
- One link per note keeps the model and the summary output unambiguous. Multiple links → multiple notes.

#### 4.4.1 Multi-line notes

The capture field is an **auto-growing textarea**, one row tall when empty, expanding as you type and snapping back after a save. It grows to about eight lines and then scrolls internally — the field should never push the note list off the screen.

**Key behavior:**

| Key | Action |
|-----|--------|
| `Enter` | **Save.** Unchanged — the one-keystroke path is the whole product |
| `Shift+Enter` | Insert a line break |
| `Alt/Opt+Enter` | Insert a line break (alias, for muscle memory from other apps) |
| `Esc` | Clear the field and any attached link, or cancel an edit |

Enter-saves rather than Enter-newlines is the deliberate choice. Most notes are one line, and making the common case cost a modifier to save something that can't be typed at all today would be the wrong trade. The placeholder names `Shift+Enter` so the capability is discoverable without documentation.

**Downstream handling.** Line breaks are preserved verbatim in storage and in both note lists (rendered with `white-space: pre-wrap`), and survive the file round-trip. Two places deliberately reshape them:

- **Grouped-list Markdown** indents continuation lines by two spaces so a multi-line note stays inside its bullet rather than breaking the list:

  ```markdown
  - Cut over the staging cluster
    Zero downtime; rollback rehearsed twice (Mon Jul 20)
  ```

- **AI narrative** collapses breaks — prose has no line breaks — and the prompt is instructed to treat a multi-line note as one item, not several.

Confirmation dialogs (discard, delete) flatten line breaks to spaces and truncate at ~80 characters, so a long note doesn't produce an unreadable alert.

**Length** stays a soft ~500-character guide rather than a hard limit. Multi-line makes it easier to overrun, and the constraint is still a feature — but a note you can't finish is worse than a long one.

### 4.5 The project note list — where editing and deleting live

Below the capture controls sits the list of notes already logged **this week for the selected project**, newest first. It changes as you change projects. It exists for three reasons: you can see what you've already said (so you don't duplicate), you can fix a typo, and you can remove something you shouldn't have written.

**Click a note to edit it.**

| Situation | Behavior |
|-----------|----------|
| Capture field is empty | The note loads into the field — body and link — and the app enters editing mode |
| Capture field has unsaved text or a link | **Confirm first**, quoting what would be discarded: *"You have unsaved text: '…'. Discard it and edit this note instead?"* |
| Already editing a different note | **Confirm first** — *"You're editing another note. Discard those changes?"* |
| You switch projects mid-edit | **Confirm first**, naming both projects |

**Editing mode** is unmistakable: a labelled bar appears above the field ("Editing the note from Thu — Enter updates it, Esc cancels"), the capture box takes the accent border, the row highlights in the list, and the Save button reads **Update**. `Esc` or Cancel exits without saving.

Updating leaves `createdAt` untouched, so a note keeps its true day and week no matter when you fix a typo in it.

**Deleting** is a `×` on each row, revealed on hover, and always **confirms with the note's text quoted back**. Deletion is the one destructive action in the app; it should cost a deliberate second click and it should show you exactly what you're about to lose.

Clicking a link chip inside a row opens the link and does *not* start an edit.

### 4.6 Voice

- Web Speech API (`SpeechRecognition`). No key, no cost. Good in Chrome/Edge, present in Safari, absent in Firefox — the mic button hides when unsupported.
- Press mic (or `M`) → interim transcript streams into the field → silence ~2s or press again to stop.
- Transcript is left **editable and unsaved**. Never save on voice alone; a misheard note is worse than no note.
- Requires HTTPS and a one-time mic permission grant.

### 4.7 Save behavior

`Enter` saves, clears the field and any attached link, collapses the field back to one row, keeps focus, flashes a confirmation. The selected project persists. Write is optimistic in the UI, committed to IndexedDB immediately, and queued for file sync (§6).

### 4.8 Chrome widget — keyboard-first capture (v2)

A companion browser extension providing a compact popup for capture-without-context-switch. This is where the **keyboard-first** design lives, and it is deliberately a different interaction model from the in-app surface above:

- **No visible project list.** A single chip showing the current project, with `#` opening a fuzzy picker: type two or three letters, `Enter`, done. Fast when you know your projects; opaque when you don't — which is exactly why it belongs in the power-user surface and not the main app.
- **Browser-level hotkey** registered via the extension's `commands` API (e.g. `Cmd+Shift+L`), working from any tab. This is the closest thing to a global hotkey available without shipping a desktop app.
- **Context awareness:** the popup pre-fills the link chip with the current tab's URL and title. Capturing "shipped this PR" while looking at the PR becomes one keystroke plus a sentence.
- **Same data store**, written through the app's origin so there is one source of truth.
- Everything else — review, summarize, settings — stays in the app. The widget captures and nothing more.

Also parked here: the open question about **note types** ("what's next", "what's blocked"). If those land, the widget's keyboard model is where a second axis can be added without cluttering the click-first surface — a modifier on save, or a `>`/`!` prefix.

---

## 5. Mode 2 — Summarize

### 5.1 Week selection and returning to now

- Header shows the week range with `←` `→` stepping.
- When the selected week is not the current one, a **"This week"** button appears in the header — always visible, one click, also bound to `T` and to `Home`. Pressing `Esc` from a past week also returns to current.
- The header is visually marked when viewing history (muted background, "Past week — read only" label) so there's never ambiguity about what you're looking at.
- Switching to Capture mode always resets the selection to the current week. You cannot leave a stale week selected behind you.
- A week dropdown lists recent weeks with note counts for direct jumps.

### 5.2 Content

- Notes grouped by project, highlights first, chronological within group, with day labels and link chips.
- Counts: notes this week, projects touched.

**Summarize is read-mostly. There is no delete here.** The only mutation available is toggling a highlight (`★`), which is a formatting decision about the output you're looking at, not a change to the record. Editing and deleting live in Capture (§4.5), next to the note, behind a confirmation.

This is a deliberate reversal from earlier drafts, which put a delete button on every row. Review is a scanning activity — you move fast down a list you're about to send — and that's exactly the wrong posture for a one-click destructive action sitting under the cursor. Moving a note between projects and backdating remain future work and, when they land, belong in Capture too.

### 5.3 Output — two forms, both always available

**Grouped list (default, offline, deterministic).** Markdown grouped by project. This is the guaranteed output and the fallback for every failure path.

```markdown
## Week of Jul 20 – Jul 26, 2026

### Atlas Migration
- Cut over the staging cluster; zero downtime (Tue Jul 21) — [runbook](https://…)
- Finished the rollback runbook and dry-ran it (Thu Jul 23)

### Q3 Hiring
- Closed the senior backend req — offer accepted (Wed Jul 22)
```

**AI narrative (optional, on demand).** "Polish with AI" rewrites the list as prose: a 1–2 sentence lead plus 2–4 sentences per project.

- User-supplied API key, stored locally, sent only to the model provider.
- Prompt constraints: preserve every fact, invent nothing, no unearned adjectives, past tense, keep links.
- Output is **editable in place**; the raw list stays visible beside it for verification.
- Any failure (no key, offline, API error) degrades to the grouped list with a dismissible notice.
- Generated summaries are cached against the week key, so a past week shows what you actually sent — not a fresh regeneration.

Two copy actions: **Copy list** (the deterministic grouped Markdown) and **Copy narrative** (the AI prose).

#### 5.3.1 The API call

A single unstreamed `POST` to the Anthropic Messages API, made directly from the page.

```
POST https://api.anthropic.com/v1/messages

content-type: application/json
x-api-key: <the user's key>
anthropic-version: 2023-06-01
anthropic-dangerous-direct-browser-access: true

{ "model": "claude-sonnet-5", "max_tokens": 1200,
  "messages": [{ "role": "user", "content": "<prompt>" }] }
```

The last header is the one people miss: **without it the browser request is refused by CORS.** Anthropic named it "dangerous" deliberately — see the security position below.

**Prompt.** The notes are sent grouped by project, highlights first, flagged with `★`, multi-line notes collapsed to one line with `/` separators, links kept as Markdown. The instructions are fixed and not user-editable:

- Preserve every fact; invent nothing — no numbers, names, dates or outcomes that aren't in the notes.
- Add no adjectives the notes don't support. *"Fixed the leak"* must not become *"heroically fixed a critical leak."*
- Past tense; person controlled by the **Summary voice** setting.
- One or two opening sentences, then one short paragraph per project in the given order, project name in bold, two to four sentences each.
- A `★` note leads its project's paragraph.
- Preserve Markdown links verbatim.
- Treat a multi-line note as one item.
- Markdown only — no preamble, no headings, no closing commentary.

The anti-embellishment rules matter more than they look. An unconstrained model will happily turn a terse factual note into something that reads well and overstates what happened — which is precisely the thing you cannot afford in a status report you're putting your name to. The grouped list stays visible beside the narrative so the source is always one glance away.

**Failure paths — all of them land on the grouped list.**

| Condition | Behavior |
|-----------|----------|
| No key set | Message naming ⚙ → AI and linking to the console. No request made |
| `401` | *"That key was rejected — check it in ⚙ → AI"* |
| `404` | *"That model name wasn't found"* |
| `429` | *"Rate limited or out of credit"* |
| Network / CORS failure | If the page is on `file://`, says so and gives the exact `python3 -m http.server` command; otherwise reports the network error |
| Empty response | *"The model returned nothing. Try again."* |

The AI is a convenience layer. Nothing about it can prevent you producing and sending a status update.

**`file://` will not work.** A page opened directly from disk has origin `null`, which the API rejects. The app must be served over http — `python3 -m http.server 8000` locally, or any static host in production. Settings detects the current protocol and shows the relevant instruction rather than making the user diagnose a CORS error.

**Security position.** A key held in the browser is readable by anyone with access to that device or profile, and by any script that gets injected into the page. This is acceptable for a single-user personal tool holding the user's own key — the blast radius is their own account, and the alternative is running a server for a local-first app. It becomes unacceptable the moment the app is shared, deployed for others, or holds a key that isn't the user's own; that case needs a thin server-side proxy so the key never reaches the client. The Settings panel states this plainly rather than burying it.

The key is written to browser storage but **stripped from the data file on every write** (§6.2), so syncing the file through Dropbox or committing it to git never leaks it.

---

## 6. Storage and file handling

Two layers, always both active when configured.

### 6.1 Layer 1 — Session/browser store (always on)

**IndexedDB** is the working store. Every write lands here first, synchronously and without network. The app is fully functional with only this layer — you can use it for weeks without ever picking a file.

`localStorage` holds UI preferences and the API key only.

### 6.2 Layer 2 — File sync (opt-in, strongly encouraged)

The user designates a **data file** — a single JSON document holding all projects, notes, and cached summaries. The app writes the full document to it after every change, debounced ~2 seconds.

- **Format:** `.json`, human-readable, schema-versioned. Default name `this-week.json`.
- **Why full-document rewrite rather than a delta log:** the data is tiny (a few hundred KB after years), and a single self-describing file that opens in any text editor is worth far more than write efficiency.
- **Where it lives is the user's business.** Put it in Dropbox/iCloud/a git repo and you get sync and version history for free without the app implementing any of it.
- **Status indicator** in the settings surface: file name, last-synced time, and a warning dot if sync is failing or no file is set.

### 6.3 The four file operations

All four live in **Settings → Storage**, never in the main path.

| Operation | Behavior | Changes sync target |
|-----------|----------|:---:|
| **New database** | Prompts for a location and filename, creates the file, and makes it the active sync target. If the browser store already holds notes, asks whether to **carry them over** or **start clean**. | yes |
| **Open database** | File picker; loads that file's contents, **replacing** the browser store. Confirms first, showing both note counts, and points at Import → Merge if combining is what was actually wanted. | yes |
| **Export** | One-off snapshot download, filename stamped with the date. For backups and for moving to another browser or machine. | no |
| **Import** | Reads a JSON file and offers **Merge** (union by note id, newer wins on collision) or **Replace**. Merge is what reconciles two machines. | no |
| **Disconnect** | Unlinks the file. The browser store keeps working; the header badge drops to "this browser only". | clears |
| **Reconnect** | Appears when a remembered handle has lost permission. One click re-grants and flushes a write. | no |

**Header status badge.** A persistent, unobtrusive indicator sits next to the settings gear and states the truth at a glance: *this browser only* (amber) · *filename · 2m ago* (green) · *reconnect filename* (amber) · *sync failed* (red). Clicking it opens Storage settings. Storage state should never be something the user has to go looking for.

### 6.4 Reconnecting on launch

File handles obtained through the File System Access API are persisted in IndexedDB, so the app remembers your file across sessions. Chrome requires a one-click permission re-grant per session; the app shows a single unobtrusive "Reconnect *this-week.json*" affordance rather than a blocking modal — you can keep working in the session store and reconnect whenever.

### 6.5 Browser support — the honest constraint

The File System Access API (`showSaveFilePicker`, `showOpenFilePicker`, persistent handles) is **Chrome/Edge/Opera only**. Safari and Firefox don't have it.

- **Where supported:** true two-way file sync as described.
- **Where not:** Storage settings degrade to download-based Export and upload-based Import, plus a nag if no export has happened in 14 days. The app still works; the durable copy is just manual.
- The Storage settings panel states which mode you're in rather than silently behaving differently.

### 6.6 Conflicts

Single user, single active file — real conflicts are rare but possible via cloud-synced folders. On load, if the file's `updatedAt` is newer than the session store's, the app prompts: keep file, keep session, or merge. No silent overwrites in either direction.

### 6.7 Durability risk

IndexedDB alone is browser-scoped and can be cleared by the user or evicted by the browser. Mitigations: request `navigator.storage.persist()` on first save; encourage file sync during onboarding; show last-sync/last-export prominently in Settings; nag if neither has happened recently. **This is the app's single biggest risk and onboarding should say so plainly.**

---

## 7. Management (Settings dialog)

A single dialog, four tabs: **Storage · Projects · AI · Preferences**. Nothing here is needed during normal daily use — but everything here is **editable in place and applied immediately**. There is no Save button and no OK/Cancel: each control writes on change, persists, and the surface behind the dialog updates live. A settings panel that looks like a control and behaves like a label is worse than no panel.

### 7.1 Storage

Sync status (file name, path, last sync, note/project counts); New database · Open database · Export · Import (§6.3); browser-support notice; `storage.persist()` state.

### 7.2 Projects

| Control | Effect |
|---------|--------|
| Name (inline text field) | Renames live; capture tiles and existing notes update immediately |
| Color swatch (click to cycle / picker) | Recolors the tile, group headers, and note dots |
| ↑ ↓ | Reorders. **This order is the tile order and the number-shortcut order** — the number badges renumber as you move rows |
| Archive / Restore | Removes from the capture row while keeping all history. If the archived project was selected, selection falls to the first active one |
| Add | Name field + button; created active and appended |

### 7.3 AI

| Control | Effect |
|---------|--------|
| API key (password field) | Stored on this device only; never written to the data file. Empty is valid — the grouped list still works |
| Model (select) | Which model the polish call uses |
| Summary voice (segmented) | First person ("I shipped…") or impersonal ("Shipped…"). Changes the prompt only, never your notes |

### 7.4 Preferences

| Control | Effect | Applies |
|---------|--------|---------|
| Theme (segmented: System / Light / Dark) | Sets `data-theme`; System follows `prefers-color-scheme` | Instantly |
| Week starts on (select: Monday / Sunday) | Changes week boundaries and therefore how notes group | Instantly; regroups existing notes, nothing is rewritten |
| Dictation (toggle) | Shows/hides the mic button and disables `M` | Instantly |
| Number shortcut (select: Auto / ⌥ / ⌘ / Off) | Which modifier selects a project. Auto resolves to ⌘ in an installed PWA, ⌥ in a browser tab | Instantly; **tile badges relabel to match** |
| Remind me to export (toggle) | Nag when no file is connected and no export in 14 days | Next check |

Below the controls: the shortcut reference (§11), showing the bindings that are actually live given the settings above, and the PWA/OS-hotkey setup instructions.

---

## 8. Week semantics

- A week runs **Monday 00:00 → Sunday 23:59**, local time (Sunday start is a setting). Key format: `2026-W30`.
- **Nothing is deleted on reset.** The "reset" is a view change: Capture always targets today's week, so Monday morning looks empty. Prior notes stay in storage.

### 8.1 A note's week is derived, never stored

The week a note belongs to is computed from `createdAt` at render time. It is **not** a field written at save time.

This matters more than it sounds. If the week were stamped on save, a note written Friday and then read after the app sat closed all weekend would still claim to be "this week," and Monday's view would open with last week's work in it. Deriving from the timestamp means the rollover happens on its own, correctly, with no scheduled job, no service worker, and no code that runs at midnight — the app can be closed for a month and still be right when it opens.

The stored `weekKey` in the data model (§10) exists only to make **backdating** explicit: a note deliberately moved into the prior week keeps its truthful `createdAt` while `weekKey` records the override. When `weekKey` is absent — the normal case — the week is derived. Changing the week-start setting therefore regroups every existing note instantly and rewrites nothing.
- **Grace period:** through Monday 23:59, Summarize's previous week remains editable and a note can be backdated into it in one click. `weekKey` is stored on the note so backdating is explicit while `createdAt` stays truthful.

---

## 9. Hotkey — the honest constraint

A browser page **cannot register an OS-global hotkey.** Three layers, in order of effort:

1. **In-app shortcuts (v1, required).** See §11. The app opens with the field focused, so opening it *is* the capture action.
2. **PWA install + OS shortcut (v1, recommended).** `manifest.webmanifest` and the icon set (§17) exist, so this path works today. Installable PWA opening in its own window; the user binds a global hotkey to it via macOS Shortcuts.app / Raycast / Alfred, or a Windows shortcut. Documented in onboarding.
3. **Browser extension (v2, optional).** A companion extension registering a browser-level command that opens a capture popup whenever the browser is running.

If a true global hotkey turns out to be non-negotiable, the correct answer is a desktop wrapper (Tauri/Electron) — the rest of this spec ports over largely unchanged, and file handling actually gets simpler.

---

## 10. Data model

```ts
type Project = {
  id: string;            // uuid
  name: string;
  color: string;         // hex
  archived: boolean;
  createdAt: string;     // ISO 8601
  sortOrder: number;
};

type Link = {
  url: string;
  label: string;         // user text, or the domain
};

type Note = {
  id: string;
  projectId: string;
  body: string;          // plain text, may contain "\n"; ~500 char soft guide
  link: Link | null;     // at most one
  highlight: boolean;
  createdAt: string;     // ISO 8601, truthful even when backdated — the week is derived from this
  weekKey?: string;      // set ONLY when backdated; absent means "derive from createdAt" (§8.1)
  source: "type" | "voice" | "paste";
  updatedAt: string;     // drives merge-on-import conflict resolution
};

type WeekSummary = {
  weekKey: string;
  markdown: string;      // AI output, user-edited
  generatedAt: string;
  model: string;
};

type Settings = {
  weekStartsOn: 0 | 1;                          // 0 = Sunday, 1 = Monday
  lastProjectId: string | null;
  voiceEnabled: boolean;
  theme: "system" | "light" | "dark";
  shortcutModifier: "auto" | "alt" | "cmd" | "off";
  summaryVoice: "first-person" | "impersonal";
  model: string;
  exportNag: boolean;
};
```

**File document format**

```jsonc
{
  "schemaVersion": 1,
  "app": "it-happened-this-week",
  "updatedAt": "2026-07-25T18:04:11.220Z",
  "projects": [ /* Project[] */ ],
  "notes":    [ /* Note[] */ ],
  "summaries":[ /* WeekSummary[] */ ]
}
```

The API key is **never** written to the data file.

**Indexes:** `notes.weekKey`, `notes.projectId`, compound `[weekKey+projectId]`.

---

## 11. Keyboard

| Key | Action | Notes |
|-----|--------|-------|
| `Alt/Opt+1…9` | Select project *n* | Works in every browser — the default binding |
| `Cmd/Ctrl+1…9` | Select project *n* | **Installed PWA only.** Browsers reserve this for tabs |
| `1…9` | Select project *n* | Only while the capture field is empty |
| `Enter` | Save note | |
| `Shift+Enter` | Line break inside a note | `Alt+Enter` also works |
| `M` | Toggle dictation | Field must be empty |
| `Esc` | Clear field and link · close dialog · return to current week | |
| `Cmd/Ctrl+Shift+Tab` | Toggle Capture ⇄ Summarize | `Tab` alone is left for normal focus traversal |
| `N` or `/` | Focus the capture field | From Summarize |
| `←` `→` | Step weeks | Summarize |
| `T` or `Home` | Return to current week | Summarize |
| `Cmd/Ctrl+,` | Settings | |
| `Cmd/Ctrl+C` | Copy summary | Summarize, nothing selected |
| `#` | Fuzzy project picker | **Chrome widget only** (§4.8) |

Note that `Tab` no longer switches modes — with a row of clickable project tiles, `Tab` has to do ordinary focus traversal or the surface isn't keyboard-accessible. Mode switching moves to `Cmd/Ctrl+Shift+Tab`.

---

## 12. Functional requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Two primary modes only: Capture and Summarize; all else behind Settings | Must |
| FR-2 | App launches into Capture with the field focused, no user action | Must |
| FR-3 | Capture always targets the current week; no week UI in Capture | Must |
| FR-4 | Enter saves to the selected project and clears the field | Must |
| FR-5 | Notes persist to IndexedDB immediately; no network dependency | Must |
| FR-6 | Last-used project persists and preselects across saves and sessions | Must |
| FR-7 | All active projects shown as clickable tiles, always visible, no menu | Must |
| FR-7a | `Alt/Opt+1…9` selects project *n*; tiles display their live binding | Must |
| FR-7b | `Cmd/Ctrl+1…9` enabled when running as an installed PWA | Should |
| FR-7c | Bare `1…9` selects project *n* while the field is empty | Should |
| FR-7d | `+ New` creates and selects a project inline, without leaving Capture | Must |
| FR-8 | A note may carry one link; pasted or typed URLs attach automatically | Must |
| FR-8a | No link button — paste is the only entry path in the main app | Must |
| FR-8b | URL is lifted out of the body; surrounding text preserved | Must |
| FR-8c | Removing a link chip returns the URL to the body text | Must |
| FR-8d | No network fetch for link titles, favicons, or previews | Must |
| FR-8k | Notes may contain line breaks; the field auto-grows and snaps back after save | Must |
| FR-8l | `Enter` saves; `Shift/Alt+Enter` inserts a line break | Must |
| FR-8m | Line breaks preserved in storage, both note lists, and the file round-trip | Must |
| FR-8n | Markdown output indents continuation lines to keep them inside the bullet | Must |
| FR-8o | Confirmation dialogs flatten and truncate note text | Should |
| FR-8e | Each tile shows its note count for the current week; zero is styled to stand out | Must |
| FR-8f | Capture lists the selected project's notes for this week, newest first | Must |
| FR-8g | Clicking a note loads it for editing; updating leaves `createdAt` unchanged | Must |
| FR-8h | Confirm before discarding unsaved input or an in-progress edit (incl. on project switch) | Must |
| FR-8i | Editing mode is visually unmistakable and cancellable via `Esc` or a Cancel control | Must |
| FR-8j | Deleting a note confirms, quoting the note's text | Must |
| FR-9 | Summarize groups by project, highlights first, chronological within group | Must |
| FR-9a | **Summarize offers no delete.** Highlight is its only mutation | Must |
| FR-10 | "This week" control returns to the current week from any past week; also `T`/`Home`/`Esc` | Must |
| FR-11 | Past weeks are visually marked as read-only | Must |
| FR-12 | Switching to Capture resets week selection to current | Must |
| FR-13 | Grouped-list summary generates offline and copies to clipboard, links included | Must |
| FR-14 | Settings dialog contains New database, Open database, Import, Export | Must |
| FR-14a | New database asks whether to carry existing notes over or start clean | Must |
| FR-14b | Open database confirms, showing both note counts, before replacing | Must |
| FR-14c | Disconnect unlinks the file without touching the browser store | Should |
| FR-15 | Designated file is written after every change, debounced; pending write flushed on unload | Must |
| FR-16 | File handle persists across sessions with a non-blocking reconnect affordance | Must |
| FR-16a | Header badge shows storage state at all times and opens Storage settings on click | Must |
| FR-16b | A note's week is derived from `createdAt` at render time, not stamped at save | Must |
| FR-16c | The API key is written to the browser store but never to the data file | Must |
| FR-17 | Import offers Merge or Replace; merge resolves by `updatedAt` | Must |
| FR-18 | Open database confirms before replacing session data | Must |
| FR-19 | Sync status (file, last sync) visible in Settings | Must |
| FR-19a | Every Settings control is editable in place and applies immediately — no Save/OK/Cancel | Must |
| FR-19b | Project rename, recolor, reorder and archive update the capture tiles live | Must |
| FR-19c | Project order in Settings determines tile order and number-shortcut assignment | Must |
| FR-19d | Changing the shortcut modifier relabels the tile badges | Must |
| FR-19e | Changing week start regroups existing notes without rewriting them | Must |
| FR-20 | Graceful degradation to Export/Import on Safari and Firefox, stated in the UI | Must |
| FR-21 | Notes editable and deletable from Capture (§4.5); moving between projects is v2 | Must |
| FR-22 | Voice capture, transcript editable before save | Should |
| FR-23 | AI narrative with user key, graceful degradation | Should |
| FR-23a | Direct browser call sends `anthropic-dangerous-direct-browser-access` | Must |
| FR-23b | Every AI failure path degrades to the grouped list with a specific, actionable message | Must |
| FR-23c | `file://` origin is detected and the fix is stated, not left as a CORS error | Must |
| FR-23d | Prompt forbids invention and unearned adjectives; not user-editable | Must |
| FR-23e | Narrative and grouped list are separately copyable | Should |
| FR-24 | Installable PWA with offline shell | Should |
| FR-25 | Highlight flag surfaces a note first in its group | Should |
| FR-26 | Backdating into the prior week through Monday | Should |
| FR-27 | Conflict prompt when the file is newer than the session store | Should |
| FR-28 | Chrome widget: keyboard-first capture, `#` picker, browser hotkey, current-tab URL prefill | Could (v2) |
| FR-29 | Note types (next / blocked) — parked for the widget's keyboard model | Could (v2) |
| FR-30 | Cloud sync / accounts | Won't (v1) |

---

## 13. Non-functional requirements

- **Latency:** interactive in under 500ms warm; save reflected in UI under 50ms; file write is async and never blocks input.
- **Offline:** fully functional except AI polish. Service worker caches the shell.
- **Privacy:** no telemetry, no server. Data leaves the device only on an explicit AI-polish request.
- **Accessibility:** full keyboard operation, visible focus rings, ARIA live region announcing saves, contrast ≥ 4.5:1.
- **Browsers:** current Chrome, Edge, Safari, Firefox. Voice degrades on Firefox; file sync degrades on Safari and Firefox.

---

## 14. Suggested technical approach

- **Stack:** React + Vite + TypeScript, Tailwind. Client-only static deploy.
- **Storage:** Dexie over IndexedDB; File System Access API for the file layer, wrapped in a `StorageAdapter` interface so the degraded path and a future desktop build are drop-in replacements.
- **State:** Zustand. Data volume is trivial (hundreds of rows/year).
- **Dates:** `date-fns` (`startOfISOWeek`, `getISOWeek`). Do not hand-roll week math.
- **Voice:** `useSpeechRecognition` hook with a capability check.
- **AI:** single client-side `POST` to the Anthropic Messages API with the user's key (§5.3.1). Requires the app to be served over http, not opened from disk. A production deployment for anyone but the key's owner should move this behind a proxy.
- **PWA:** `vite-plugin-pwa`.

---

## 15. Build order

1. **Capture mode + IndexedDB.** Project tiles with counts, capture field, save, per-project note list with edit and delete. Usable on its own.
2. **Summarize mode.** Grouping, week stepping, "This week", grouped-list output + clipboard. Read-mostly.
3. **Settings dialog + Export/Import.** Gets a durable copy in the user's hands early.
4. **File sync.** New/Open database, debounced writes, handle persistence, reconnect.
5. Paste-to-attach links, highlights, backdating.
6. Voice capture.
7. AI polish + key management.
8. PWA (also unlocks `Cmd+1…9`), persistence prompts, onboarding for the OS hotkey.
9. **v2 — Chrome widget.** Keyboard-first popup, browser hotkey, tab-URL prefill. Revisit note types here.

Ship after step 3. Steps 4–8 are additive; none block daily use.

---

## 16. Open questions

1. **Note length** — resolved: multi-line, soft ~500-char guide, no hard block (§4.4.1).
2. **Blockers / next week** — parked for the Chrome widget (§4.8), where a keyboard modifier can carry a second axis without cluttering the click-first surface. Still the biggest open product question: does a status report without "what's next" do the job?
3. **Summary voice** — first person ("I shipped") or impersonal ("Shipped")? Currently a setting; could be inferred from your edits over time.
4. **Multiple projects per note** — recommend forbidding in v1; keeps capture fast and grouping unambiguous.
5. **Empty projects in the summary** — omit, or list as "no activity"? Recommend omitting with a toggle.
6. **Multiple database files** — is there a real case for switching between them (personal vs. work), or is Open purely a recovery/migration path? If switching is routine, a recent-files list belongs in Settings.

---

## 17. Identity

### 17.1 The mark

A **tally**: four uprights crossed by a diagonal fifth. It is the oldest notation for counting things as they happen, which is precisely the behavior the app is trying to make cheap. It carries no metaphor that needs explaining, and it is not a clipboard, a checkmark, or a calendar page — the three icons every productivity tool already owns.

| | |
|---|---|
| Accent | `#b4491f` — the app's accent, used as the icon's ground |
| Mark | `#faf9f7` — the app's page background, used as the ink |
| Grid | 64 units; uprights at x = 18, 27, 36, 45 spanning y 18→46; diagonal (13,47)→(50,17); stroke 5, round caps; corner radius 14 |

### 17.2 Optical sizing

**Below 24px the mark drops from four uprights to three**, with wider gaps, a heavier pen (6.5) and a tighter corner radius (11).

This is not a detail to skip. At 16px the full five-stroke tally spans about eleven pixels — roughly two pixels per stroke including gaps — and antialiasing turns it into a grey smear. A tally that reads as a smear has failed at the one job a favicon has. Three uprights plus a diagonal still reads unmistakably as a tally and survives the size.

The `.ico` therefore contains **independently rendered** frames at 16, 32, 48, 64, 128 and 256px, rather than one image downscaled. The `.svg` keeps the full five-stroke form: browsers that use SVG favicons draw them at 2× on modern displays, where five strokes read cleanly.

### 17.3 Assets

| File | Purpose |
|------|---------|
| `icons/favicon.svg` | Master artwork; also served to browsers that support SVG favicons |
| `favicon.ico` | Six optically-sized frames; at repo root for anything that probes `/favicon.ico` |
| `icons/apple-touch-icon.png` | 180px, square and full-bleed — iOS applies its own mask, so no rounding |
| `icons/icon-192.png`, `icon-512.png` | PWA install icons, `purpose: any` |
| `icons/icon-512-maskable.png` | Artwork inset to 62% for Android's 80% safe zone, `purpose: maskable` |
| `manifest.webmanifest` | Name, colors, `display: standalone`, icon set |
| `icons/render.py`, `icons/make_ico.py` | Regenerate every raster from the same geometry |

Rasters are generated at 4× and downsampled with Lanczos; `make_ico.py` packs the ICO container by hand because Pillow's writer rescales from a single source and would discard the per-size tuning.

### 17.4 Consequences

Shipping the manifest makes the app installable, which is what unlocks `Cmd/Ctrl+1…9` for project switching (§4.3) — a standalone window has no tab strip to claim those bindings. The icon work and the keyboard work turn out to be the same piece of work.
