#!/usr/bin/env python3
"""Issue #43 Chromium input/change probe at the Stage 14 implementation tree.

Does not modify explorer behavior. Generates a page from render_explorer,
dispatches view change and search input, and dumps visibility via Chromium.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from memory_infra.explorer import render_explorer

ROOT = Path(__file__).resolve().parents[1]
CHROMIUM = "/usr/bin/chromium"
CASES = (
    "all-empty",
    "all+same-goal",
    "all+referential.same_thread",
    "all+rel-merge",
    "all+both-seen",
    "all+left claim",
    "all+e1",
    "all+not-a-match",
    "thread-empty",
    "thread+same-goal",
    "event-empty",
    "event+both-seen",
    "contradiction-empty",
    "contradiction+both-seen",
    "contradiction+same-goal",
)


def graph() -> dict:
    return {
        "read_only": True,
        "owner": "mechanism",
        "nodes": [
            {"kind": "thread", "id": "th-1", "label": "thread alpha"},
            {"kind": "thread", "id": "th-2", "label": "thread beta"},
            {"kind": "event", "id": "th-1", "observation": "same-id event"},
            {"kind": "event", "id": "e1", "observation": "left claim"},
            {"kind": "event", "id": "e2", "observation": "right claim"},
            {"kind": "state", "id": "e1", "contradiction_history": ["rel-con"]},
            {"kind": "point", "id": "e1", "content": "not an endpoint"},
        ],
        "edges": [
            {
                "relation_id": "rel-merge",
                "source_id": "th-1",
                "target_id": "th-2",
                "relation_type": "referential.same_thread",
                "evidence_ref": "same-goal",
            },
            {
                "relation_id": "rel-con",
                "source_id": "e1",
                "target_id": "e2",
                "relation_type": "evidential.contradicts",
                "evidence_ref": "both-seen",
            },
        ],
    }


PROBE = r"""
<script id="issue43-probe">
(function(){
function shown(el){return !!(el && !el.classList.contains('is-hidden'));}
function edge(id){return document.querySelector('line.edge[data-relation-id="'+id+'"]');}
function label(id){return document.querySelector('text.edge-label[data-relation-id="'+id+'"]');}
function inspector(id){return document.querySelector('aside.inspector article[data-relation-id="'+id+'"]');}
function node(kind,id){return document.querySelector('a.node[data-kind="'+kind+'"][data-id="'+id+'"]');}
function setView(v){
  var el=document.querySelector('input[name=view][value="'+v+'"]');
  el.checked=true;
  el.dispatchEvent(new Event('change',{bubbles:true}));
}
function setQ(q){
  var el=document.querySelector('input[name=q]');
  el.value=q;
  el.dispatchEvent(new Event('input',{bubbles:true}));
}
function snap(name){
  var rows=[
    ['rel-merge-edge', shown(edge('rel-merge'))],
    ['rel-merge-label', shown(label('rel-merge'))],
    ['rel-merge-inspector', shown(inspector('rel-merge'))],
    ['rel-con-edge', shown(edge('rel-con'))],
    ['rel-con-label', shown(label('rel-con'))],
    ['rel-con-inspector', shown(inspector('rel-con'))],
    ['thread:th-1', shown(node('thread','th-1'))],
    ['thread:th-2', shown(node('thread','th-2'))],
    ['event:th-1', shown(node('event','th-1'))],
    ['event:e1', shown(node('event','e1'))],
    ['event:e2', shown(node('event','e2'))],
    ['state:e1', shown(node('state','e1'))],
    ['point:e1', shown(node('point','e1'))]
  ];
  return name+'\t'+rows.map(function(row){return row[0]+'='+(row[1]?'1':'0');}).join(' ');
}
var cases=[
  ['all',''],
  ['all','same-goal'],
  ['all','referential.same_thread'],
  ['all','rel-merge'],
  ['all','both-seen'],
  ['all','left claim'],
  ['all','e1'],
  ['all','not-a-match'],
  ['thread',''],
  ['thread','same-goal'],
  ['event',''],
  ['event','both-seen'],
  ['contradiction',''],
  ['contradiction','both-seen'],
  ['contradiction','same-goal']
];
var names=['all-empty','all+same-goal','all+referential.same_thread','all+rel-merge','all+both-seen','all+left claim','all+e1','all+not-a-match','thread-empty','thread+same-goal','event-empty','event+both-seen','contradiction-empty','contradiction+both-seen','contradiction+same-goal'];
var lines=[];
cases.forEach(function(item, i){
  setView(item[0]);
  setQ(item[1]);
  lines.push(snap(names[i]));
});
var pre=document.createElement('pre');
pre.id='probe-out';
pre.textContent=lines.join('\n');
document.body.appendChild(pre);
})();
</script>
"""


def main() -> int:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    page = render_explorer(graph())
    if "</body>" not in page:
        print("render_explorer page has no body", file=sys.stderr)
        return 2
    page = page.replace("</body>", PROBE + "</body>", 1)
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "explorer.html"
        html_path.write_text(page, encoding="utf-8")
        cmd = [
            CHROMIUM,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--virtual-time-budget=5000",
            "--dump-dom",
            html_path.as_uri(),
        ]
        print("HEAD", head)
        print("COMMAND", " ".join(cmd))
        proc = subprocess.run(cmd, text=True, capture_output=True)
        print("CHROMIUM_EXIT", proc.returncode)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr)
            return proc.returncode
        dom = proc.stdout
        start = dom.find('<pre id="probe-out">')
        end = dom.find("</pre>", start)
        if start < 0 or end < 0:
            print("probe-out missing", file=sys.stderr)
            sys.stderr.write(dom[-2000:])
            return 3
        body = dom[start + len('<pre id="probe-out">') : end]
        body = body.replace("<", "<").replace(">", ">").replace("&", "&")
        print("PROBE_OUTPUT")
        print(body)
        expected = {
            "all-empty": "rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=1 thread:th-2=1 event:th-1=1 event:e1=1 event:e2=1 state:e1=1 point:e1=1",
            "all+same-goal": "rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
            "all+referential.same_thread": "rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
            "all+rel-merge": "rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
            "all+both-seen": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
            "all+left claim": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=1 event:e2=0 state:e1=0 point:e1=0",
            "all+e1": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=1 event:e2=0 state:e1=1 point:e1=1",
            "all+not-a-match": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
            "thread-empty": "rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=1 thread:th-2=1 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
            "thread+same-goal": "rel-merge-edge=1 rel-merge-label=1 rel-merge-inspector=1 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
            "event-empty": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=1 event:e1=1 event:e2=1 state:e1=0 point:e1=0",
            "event+both-seen": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
            "contradiction-empty": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=1 event:e2=1 state:e1=0 point:e1=0",
            "contradiction+both-seen": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=1 rel-con-label=1 rel-con-inspector=1 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=1 event:e2=1 state:e1=0 point:e1=0",
            "contradiction+same-goal": "rel-merge-edge=0 rel-merge-label=0 rel-merge-inspector=0 rel-con-edge=0 rel-con-label=0 rel-con-inspector=0 thread:th-1=0 thread:th-2=0 event:th-1=0 event:e1=0 event:e2=0 state:e1=0 point:e1=0",
        }
        failed = 0
        seen = set()
        for line in body.splitlines():
            if not line.strip():
                continue
            name, rest = line.split("\t", 1)
            seen.add(name)
            if expected[name] != rest:
                print("MISMATCH", name, file=sys.stderr)
                print(" expected", expected[name], file=sys.stderr)
                print(" actual  ", rest, file=sys.stderr)
                failed += 1
        missing = [name for name in CASES if name not in seen]
        if missing:
            print("MISSING", ",".join(missing), file=sys.stderr)
            failed += len(missing)
        print("PROBE_ASSERT_EXIT", 1 if failed else 0)
        return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
