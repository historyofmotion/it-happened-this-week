# It Happened This Week

A single-user web app for capturing work accomplishments as they happen, organized by project, and rolling them up into a weekly status report.

The bet: status reports fail because logging is expensive at the moment of accomplishment and impossible to reconstruct on Friday. So the capture path has to be near-zero friction — open, type or speak one line, done.

No accounts. No server. No telemetry. Your notes stay on your machine.

---

## Try it

```bash
git clone https://github.com/<you>/it-happened-this-week.git
cd it-happened-this-week
python3 -m http.server 8000
```

Then open <http://localhost:8000/it-happened-this-week-mockup.html>.

**Serve it over http rather than opening the file directly.** Everything works from a `file://` URL except the AI summary — the Anthropic API rejects requests with a `null` origin. The app detects this and tells you, but it's easier to start the right way.

---

## Two modes, and nothing else

**Capture** — every project is a tile with a count of what you've logged this week. A dashed `0` is the project that needs attention. Type, hit Enter, done. Capture always writes to *now*; there's no week selector, so you can't file something into the wrong week.

**Summarize** — the week grouped by project, plus the output you actually send. Read-mostly: the only thing you can change here is which notes are highlighted.

Everything else — projects, storage, keys, preferences — lives behind the gear and isn't needed day to day.

---

## What it does

- **One-line capture** with the last-used project preselected. `Alt+1`–`9` switches projects (`Cmd` when installed as a PWA, since browsers reserve `Cmd+1–9` for tabs).
- **Multi-line notes** — `Enter` saves, `Shift+Enter` breaks a line.
- **Paste a URL** anywhere in the field and it lifts itself out into a link chip. No button, no title fetch, no network call between you and a saved note.
- **Dictation** via the Web Speech API. The transcript is left editable — a misheard note is worse than no note.
- **Weekly summary** in two forms: a deterministic grouped list that always works offline, and an optional AI narrative.
- **Every past week** stays readable, one click back to now.

## Storage

Two layers:

1. **Browser storage** — always on, survives refreshes, works offline. The app is fully usable before you ever pick a file.
2. **A JSON file on disk** — opt-in, rewritten after every change. Put it in Dropbox or a git repo and you get sync and version history without the app implementing either.

Settings → Storage has New database, Open database, Import (merge or replace) and Export. Live file sync uses the File System Access API, which is Chrome/Edge/Opera only; Safari and Firefox fall back to manual Export/Import and the panel says so.

`this-week-sample.json` in this repo is fake data you can load via **Open database** to see the app populated.

## AI summary (optional)

The grouped list is generated locally and always works. The AI narrative is a convenience layer on top.

1. Create a key at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys).
2. Paste it into ⚙ → AI.
3. Serve the app over http (see above).

The prompt is fixed and deliberately constrained: preserve every fact, invent nothing, add no adjectives the notes don't support, keep links, treat a multi-line note as one item. An unconstrained model will happily turn a terse note into something that reads well and overstates what happened — the one thing you can't afford in a report going out under your name. The raw list stays visible beside the narrative so the source is always a glance away.

Every failure path — no key, bad key, wrong model, rate limit, offline — lands back on the grouped list with a specific message.

### On browser-held API keys

The key is stored in browser storage and sent only to Anthropic. It is **stripped from the data file on every write**, so syncing that file through Dropbox or committing it to git won't leak it.

That said: a key in a browser is readable by anyone with access to that device or profile. Acceptable for a personal tool holding your own key. **Not** acceptable for anything shared or deployed — that needs a small server-side proxy so the key never reaches the client.

## Known limits

- **No global hotkey.** A web page can't register one. Install as a PWA and bind an OS shortcut to the window; a browser extension is planned. If a true global hotkey is non-negotiable, this wants to be a desktop app.
- **Browser storage can be cleared** by you or evicted by the browser. Link a data file and keep it somewhere backed up.
- **Live file sync is Chromium-only.**
- **Firefox has no Web Speech API**, so dictation is hidden there.

## Status

Working prototype in a single HTML file, plus a full specification in [`it-happened-this-week-spec.md`](./it-happened-this-week-spec.md) covering the data model, storage design, prompt, keyboard map, requirements and open questions.

The open question worth arguing about: real status reports usually carry *what's next* and *what's blocked*, and this only captures what happened. Whether those belong as note types on the same fast capture path is unresolved — see §16 of the spec.

## License

Apache License 2.0 — see [LICENSE](./LICENSE) and [NOTICE](./NOTICE).
