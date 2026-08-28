#!/usr/bin/env python3
"""A federated tick-network node: this repo's own append-only chain, keyed to the
global tick spine at kody-w/dogg.

Every run reads the spine's current tick anchor, takes this node's themed snapshot of
keyless public APIs, and appends one frame referencing that tick. Different repos, run
by different people, each with their own outlook — all joinable on the tick key. To
start your own node: fork this repo, edit THEME/STREAM/SOURCES below, enable the
scheduled workflow. Frames verify with the reference implementation (tools/rapp.py,
from kody-w/rapp-1); CI re-verifies the whole chain on every push.

THIS NODE — canon: what our rules were, at each tick, provably. Each frame hashes
CONSTITUTION.md (kody-w/RAR), SPEC.md (kody-w/rapp-1), and PROTOCOL.md (kody-w/dogg) as
of the moment fetched, plus the count of "## Article" headings in the constitution — so
a grandchild reading this chain decades from now can prove exactly which text governed
at any given tick, byte for byte, without trusting anyone's memory of it.
"""
import hashlib
import json, sys, pathlib, datetime, urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import rapp as R
import chainio

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPINE_HEAD = "https://raw.githubusercontent.com/kody-w/dogg/main/ticks/HEAD.json"
TIMEOUT = 8

# ---- edit these three for your node -------------------------------------------------
THEME = "canon"                       # also the data directory name
STREAM = "canon:@kody-w/dogg-canon"   # your stream id (your repo, your name)
# SOURCES: name -> zero-arg callable returning a SMALL dict of facts.
# rapp/1 canonical hashing forbids floats: numeric facts ride as strings or ints.
# -------------------------------------------------------------------------------------

def utc():
    n = datetime.datetime.now(datetime.timezone.utc)
    return n.strftime("%Y-%m-%dT%H:%M:%S.") + f"{n.microsecond // 1000:03d}Z"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"tick-node-{THEME}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())

def get_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"tick-node-{THEME}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8")

def _doc_facts(url, count_articles=False):
    text = get_text(url)
    octets = text.encode("utf-8")
    out = {"sha256": hashlib.sha256(octets).hexdigest(), "bytes": len(octets)}
    if count_articles:
        out["articles"] = sum(1 for line in text.splitlines() if line.startswith("## Article"))
    return out

SOURCES = {
    "rar_constitution": lambda: _doc_facts(
        "https://raw.githubusercontent.com/kody-w/RAR/main/CONSTITUTION.md", count_articles=True),
    "rapp1_spec": lambda: _doc_facts(
        "https://raw.githubusercontent.com/kody-w/rapp-1/main/SPEC.md"),
    "dogg_protocol": lambda: _doc_facts(
        "https://raw.githubusercontent.com/kody-w/dogg/main/PROTOCOL.md"),
}

def load_chain(d):
    return chainio.load_chain(d)

def main():
    spine = get(SPINE_HEAD)
    tick_n, tick_hash = spine["count"] - 1, spine["head_frame"]
    d = ROOT / THEME
    d.mkdir(exist_ok=True)
    chain = load_chain(d)
    head = chain[-1] if chain else None
    if head is not None and head["payload"].get("tick") == tick_n:
        print(f"{THEME}: tick {tick_n} already recorded — nothing to do")
        return
    data, failed = {}, []
    for name, fn in SOURCES.items():
        try:
            data[name] = fn()
        except Exception:
            failed.append(name)
    payload = {"tick": tick_n, "tick_frame": tick_hash, "spine": "kody-w/dogg",
               "fetched_utc": utc(), THEME: data, "sources_failed": failed}
    if head is None:
        payload["about"] = (f"A federated node of the global tick network: this repo's "
                            f"own {THEME} outlook, one frame per observed tick, keyed to "
                            "the spine's tick anchors so it joins every other node's "
                            "data on the same clock.")
    f = R.build_frame(f"{THEME}.snapshot", STREAM, (head["seq"] + 1) if head else 0,
                      utc(), payload, prev=(head["payload_hash"] if head else None))
    ok, step, why = R.verify_frame(f, head=head, stream_id_of_record=STREAM)
    if not ok:
        raise ValueError(f"refusing invalid frame: {step}: {why}")
    chainio.append_frame(d, f, STREAM)
    print(f"{THEME} frame {f['seq']} @ spine tick {tick_n}: {', '.join(data) or 'nothing'}"
          + (f" (failed: {', '.join(failed)})" if failed else ""))

if __name__ == "__main__":
    main()
