# dogg-canon — a federated node of the global tick network

**What our rules were, at each tick, provably.**

This repo keeps its own append-only chain of rapp/1 frames in `canon/`. Once a day a
GitHub Action reads the current tick anchor from the spine at
[kody-w/dogg](https://github.com/kody-w/dogg), fetches three governing texts —
[`CONSTITUTION.md`](https://github.com/kody-w/RAR/blob/main/CONSTITUTION.md) (kody-w/RAR),
[`SPEC.md`](https://github.com/kody-w/rapp-1/blob/main/SPEC.md) (kody-w/rapp-1), and
[`PROTOCOL.md`](https://github.com/kody-w/dogg/blob/main/PROTOCOL.md) (kody-w/dogg) — and
appends one frame recording each document's SHA-256 and byte length, plus the count of
`## Article` headings in the constitution, all referenced to that tick. "Right now" web
views only show the current text; the network keeps every past text a working link
away, hashed at the moment it governed.

## Why this matters

Constitutions, specs, and protocols are living documents — they get amended. Nothing
on GitHub stops a rewrite of history: force-pushes happen, branches get rebased, "the
current file" is whatever HEAD says today. This chain is a second, independent witness:
an append-only, hash-verified record of exactly what those three files' bytes were on
each day this node ran, tied to the same global tick every other node in the network
shares. A grandchild reading this chain in 2076 doesn't have to trust anyone's memory
of "what the rules used to say" — they can fetch this repo, recompute the hashes
themselves with `tools/rapp.py`, and *prove* which text governed at any recorded tick.

## Precision and limits

- **Cadence:** one frame per day (`0 6 * * *` UTC). Canon moves slowly by nature —
  constitutions don't change hour to hour — so this node trades the reference node's
  half-hour beat for a daily one. A same-day edit and revert between two collection
  runs would not appear in this chain; only what was live at collection time is
  recorded.
- **What's proven:** the exact byte content of each document *as this node fetched it*
  (SHA-256 over the raw UTF-8 bytes from GitHub's raw content server), not GitHub's own
  history, not intent, not any signature from the document's authors. If GitHub's raw
  endpoint served something transient or an edit landed mid-fetch, that's what gets
  hashed — the frame is honest about what it observed, not about what "should" have
  been true.
- **Article count:** counted by a plain `^## Article` line match against
  `CONSTITUTION.md`'s Markdown, not a parser aware of nesting or renumbering. If the
  document's heading convention changes, this number tracks the convention at hash
  time, not some fixed schema.
- **No secrets, no PII:** every source here is a public raw GitHub URL; the payload
  carries only hashes, byte counts, and a heading count — no credentials, no personal
  data, ever.

**Verify it yourself:** `python3 tools/verify_thread.py` re-checks every frame with the
reference implementation from [kody-w/rapp-1](https://github.com/kody-w/rapp-1). CI runs
the same oracle on every push.

**Start your own node:** fork this repo, edit `THEME` / `STREAM` / `SOURCES` at the top
of `tools/collect.py` (keyless https APIs, small factual payloads, numbers as strings),
and enable the scheduled workflow. Your chain, your outlook, same clock — announce it on
the spine's registry ([kody-w/dogg](https://github.com/kody-w/dogg) issues) so agents
can find it.

## Trust

<!--trust-->
No ratings yet — used this chain? [Rate it](../../issues/new?template=rate.yml): valid ratings publish automatically as verifiable frames.
<!--/trust-->
