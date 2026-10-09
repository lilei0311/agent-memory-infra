"""Stage 14 read-only Visual Memory Explorer.

Presentation over a Stage 13 read_graph projection. It does not allocate
ids, persist a graph, or mutate mechanism state.
"""

from __future__ import annotations

import html
from typing import Mapping

NODE_KINDS = ("event", "point", "state", "thread")
EDGE_KINDS = (
    "contextual.changed_context",
    "causal.caused",
    "causal.caused_by",
    "causal.enabled",
    "causal.prevented",
    "evidential.contradicts",
    "referential.revisits",
    "referential.same_thread",
    "temporal.before",
)
SHAPE = {
    "point": "circle",
    "event": "rectangle",
    "thread": "rounded-rectangle",
    "state": "diamond",
}
COLUMN = {"point": 80, "event": 280, "thread": 480, "state": 680}


def render_explorer(graph: Mapping) -> str:
    """Deterministic HTML/SVG for one projection. Input is not mutated."""

    if graph.get("read_only") is not True or graph.get("owner") != "mechanism":
        raise ValueError("explorer requires a mechanism-owned read-only projection")
    nodes = [dict(row) for row in graph.get("nodes", [])]
    edges = [dict(row) for row in graph.get("edges", [])]
    nodes.sort(key=lambda row: (row["kind"], row["id"]))
    edges.sort(key=lambda row: (row["relation_type"], row["relation_id"]))
    _mark_contradiction_endpoints(nodes, edges)
    positions = _positions(nodes)
    body = "\n".join(
        [
            _status(),
            _nav(),
            _canvas(nodes, edges, positions),
            _inspector(nodes, edges),
        ]
    )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        "<title>Visual Memory Explorer</title>"
        f"<style>{_css()}</style></head>"
        f'<body data-read-only="true" data-owner="mechanism">\n{body}\n'
        f"<script>{_filter_script()}</script>\n</body></html>\n"
    )


def presentation_key(kind: str, mechanism_id: str) -> str:
    """Deterministic DOM key. Displayed mechanism id is not rewritten."""

    raw = f"{kind}:{mechanism_id}"
    return "n-" + "".join(
        ch if ch.isalnum() or ch in "-_" else f"_{ord(ch):x}_" for ch in raw
    )



def _mark_contradiction_endpoints(nodes: list[dict], edges: list[dict]) -> None:
    endpoint_ids = {
        edge["source_id"]
        for edge in edges
        if edge["relation_type"] == "evidential.contradicts"
    } | {
        edge["target_id"]
        for edge in edges
        if edge["relation_type"] == "evidential.contradicts"
    }
    for row in nodes:
        row["_contradiction_endpoint"] = row["id"] in endpoint_ids


def _search_text(row: dict) -> str:
    parts = []
    for key, value in row.items():
        if key.startswith("_"):
            continue
        parts.append(str(key))
        parts.append(_text(value))
    return " ".join(parts)


def _filter_script() -> str:
    """Display-only filter. Does not write memory, storage, or network."""

    return """
(function(){
function q(){var el=document.querySelector('input[name=q]');return ((el&&el.value)||'').trim().toLowerCase();}
function view(){var el=document.querySelector('input[name=view]:checked');return el?el.value:'all';}
function text(el){return (el.getAttribute('data-text')||el.textContent||'').toLowerCase();}
function hit(el,query){if(!query)return true;var id=(el.getAttribute('data-id')||'').toLowerCase();return id.indexOf(query)!==-1||text(el).indexOf(query)!==-1;}
function hide(el,on){el.classList.toggle('is-hidden',on);}
function articles(){return document.querySelectorAll('aside.inspector article');}
function apply(){
var selected=view();var query=q();var visible={};
document.querySelectorAll('a.node').forEach(function(node){
var kind=node.getAttribute('data-kind');var id=node.getAttribute('data-id');
var inView=selected==='all'||(selected==='thread'&&kind==='thread')||(selected==='event'&&kind==='event')||(selected==='contradiction'&&node.getAttribute('data-contradiction-endpoint')==='true');
var show=inView&&hit(node,query);visible[kind+':'+id]=show;hide(node,!show);});
if(selected==='contradiction'){
document.querySelectorAll('line.edge[data-contradiction=true]').forEach(function(edge){
var source=edge.getAttribute('data-source-id');var target=edge.getAttribute('data-target-id');var related=hit(edge,query);
articles().forEach(function(article){if(article.getAttribute('data-relation-id')===edge.getAttribute('data-relation-id'))related=related||hit(article,query);});
document.querySelectorAll('a.node[data-contradiction-endpoint=true]').forEach(function(node){if(node.getAttribute('data-id')===source||node.getAttribute('data-id')===target)related=related||hit(node,query);});
if(related){document.querySelectorAll('a.node').forEach(function(node){if(node.getAttribute('data-id')===source||node.getAttribute('data-id')===target){hide(node,false);visible[node.getAttribute('data-kind')+':'+node.getAttribute('data-id')]=true;}});}});
}
document.querySelectorAll('line.edge').forEach(function(edge){
var sourceKind=edge.getAttribute('data-source-kind');var targetKind=edge.getAttribute('data-target-kind');
var source=edge.getAttribute('data-source-id');var target=edge.getAttribute('data-target-id');
var contradiction=edge.getAttribute('data-contradiction')==='true';
var inView=selected==='all'||(selected==='contradiction'&&contradiction)||(selected==='event'&&sourceKind==='event'&&targetKind==='event')||(selected==='thread'&&sourceKind==='thread'&&targetKind==='thread');
var show=inView&&visible[sourceKind+':'+source]&&visible[targetKind+':'+target];
hide(edge,!show);
document.querySelectorAll('text.edge-label').forEach(function(label){if(label.getAttribute('data-relation-id')===edge.getAttribute('data-relation-id'))hide(label,!show);});
});
articles().forEach(function(article){
var kind=article.getAttribute('data-kind');var id=article.getAttribute('data-id');
var contradiction=article.getAttribute('data-contradiction')==='true';
var show=false;
if(kind){show=!!visible[kind+':'+id];}
else if(contradiction&&selected==='contradiction'){
var source=article.getAttribute('data-source-id');var target=article.getAttribute('data-target-id');
show=Object.keys(visible).some(function(key){return visible[key]&&(key.slice(key.indexOf(':')+1)===source||key.slice(key.indexOf(':')+1)===target);});
}else if(selected==='all'){show=hit(article,query);}
hide(article,!show);
});
}
document.querySelectorAll('input[name=view],input[name=q]').forEach(function(el){el.addEventListener('change',apply);el.addEventListener('input',apply);});
apply();
})();
""".strip()


def _positions(nodes: list[dict]) -> dict[tuple[str, str], tuple[int, int]]:
    counts: dict[str, int] = {}
    placed: dict[tuple[str, str], tuple[int, int]] = {}
    for row in nodes:
        kind = row["kind"]
        index = counts.get(kind, 0)
        counts[kind] = index + 1
        placed[(kind, row["id"])] = (COLUMN.get(kind, 40), 70 + index * 90)
    return placed


def _endpoint(positions: dict[tuple[str, str], tuple[int, int]], mechanism_id: str):
    matches = [
        (kind, pos)
        for (kind, mid), pos in positions.items()
        if mid == mechanism_id
    ]
    return matches


def _status() -> str:
    return (
        '<header class="status" role="status">'
        "READ-ONLY. This explorer cannot mutate memory."
        "</header>"
    )


def _nav() -> str:
    filters = (
        ("all", "All memories"),
        ("thread", "Threads"),
        ("event", "Events"),
        ("contradiction", "Contradictions"),
    )
    controls = []
    for name, label in filters:
        checked = " checked" if name == "all" else ""
        controls.append(
            f'<label class="filter">{html.escape(label)}'
            f'<input type="radio" name="view" value="{name}"{checked}></label>'
        )
    return (
        '<nav class="nav" aria-label="Memory views">'
        "<p>What does the Agent remember?</p>"
        + "".join(controls)
        + '<label class="search">Search'
        '<input type="search" name="q" placeholder="filter by id or text"></label>'
        "</nav>"
    )


def _canvas(nodes, edges, positions) -> str:
    parts = ['<main class="canvas" aria-label="Memory graph">']
    parts.append('<svg viewBox="0 0 860 640" role="img" aria-label="Memory graph">')
    for edge in edges:
        sources = _endpoint(positions, edge["source_id"])
        targets = _endpoint(positions, edge["target_id"])
        if not sources or not targets:
            continue
        # Geometry only. Shared mechanism ids stay separate nodes.
        source_kind, source = sources[0]
        target_kind, target = targets[0]
        relation_type = edge["relation_type"]
        contradiction = "true" if relation_type == "evidential.contradicts" else "false"
        css = "edge contradiction" if contradiction == "true" else "edge"
        parts.append(
            f'<line class="{css}" x1="{source[0]}" y1="{source[1]}" '
            f'x2="{target[0]}" y2="{target[1]}" '
            f'data-relation-id="{html.escape(edge["relation_id"])}" '
            f'data-relation-type="{html.escape(relation_type)}" '
            f'data-source-id="{html.escape(edge["source_id"])}" '
            f'data-target-id="{html.escape(edge["target_id"])}" '
            f'data-source-kind="{html.escape(source_kind)}" '
            f'data-target-kind="{html.escape(target_kind)}" '
            f'data-contradiction="{contradiction}" />'
        )
        label_x = (source[0] + target[0]) // 2
        label_y = (source[1] + target[1]) // 2
        parts.append(
            f'<text class="edge-label" x="{label_x}" y="{label_y}" '
            f'data-relation-id="{html.escape(edge["relation_id"])}" '
            f'data-relation-type="{html.escape(relation_type)}" '
            f'data-contradiction="{contradiction}">'
            f'{html.escape(relation_type)}</text>'
        )
    for row in nodes:
        x, y = positions[(row["kind"], row["id"])]
        parts.append(_node(row, x, y))
    parts.append("</svg></main>")
    return "\n".join(parts)


def _node(row: dict, x: int, y: int) -> str:
    kind = row["kind"]
    label = html.escape(f'{kind} {row["id"]}')
    anchor = presentation_key(kind, row["id"])
    searchable = html.escape(_search_text(row), quote=True)
    endpoint = "true" if row.get("_contradiction_endpoint") else "false"
    attrs = (
        f'data-kind="{html.escape(kind)}" data-shape="{SHAPE[kind]}" '
        f'data-id="{html.escape(row["id"])}" data-anchor="{anchor}" '
        f'data-contradiction-endpoint="{endpoint}" '
        f'data-text="{searchable}" '
        f'href="#inspect-{anchor}"'
    )
    if kind == "point":
        shape = f'<circle cx="{x}" cy="{y}" r="22" />'
    elif kind == "event":
        shape = f'<rect x="{x-28}" y="{y-16}" width="56" height="32" />'
    elif kind == "thread":
        shape = f'<rect x="{x-32}" y="{y-16}" width="64" height="32" rx="12" />'
    else:
        shape = f'<polygon points="{x},{y-20} {x+24},{y} {x},{y+20} {x-24},{y}" />'
    return (
        f'<a class="node" {attrs}>{shape}'
        f'<text x="{x}" y="{y+36}">{label}</text></a>'
    )


def _inspector(nodes, edges) -> str:
    blocks = ['<aside class="inspector" aria-label="Evidence inspector">']
    blocks.append("<h2>Why is this memory here?</h2>")
    for row in nodes:
        fields = "".join(
            f"<dt>{html.escape(key)}</dt><dd>{html.escape(_text(value))}</dd>"
            for key, value in row.items()
            if not str(key).startswith("_")
        )
        anchor = presentation_key(row["kind"], row["id"])
        endpoint = "true" if row.get("_contradiction_endpoint") else "false"
        blocks.append(
            f'<article id="inspect-{anchor}" data-anchor="{anchor}" '
            f'data-kind="{html.escape(row["kind"])}" '
            f'data-id="{html.escape(row["id"])}" '
            f'data-contradiction-endpoint="{endpoint}" '
            f'data-text="{html.escape(_search_text(row), quote=True)}">'
            f"<h3>{html.escape(row['kind'])} {html.escape(row['id'])}</h3>"
            f"<dl>{fields}</dl></article>"
        )
    for edge in edges:
        fields = "".join(
            f"<dt>{html.escape(key)}</dt><dd>{html.escape(_text(value))}</dd>"
            for key, value in edge.items()
        )
        edge_anchor = presentation_key("edge", edge["relation_id"])
        contradiction = "true" if edge["relation_type"] == "evidential.contradicts" else "false"
        blocks.append(
            f'<article id="inspect-{edge_anchor}" data-anchor="{edge_anchor}" '
            f'data-relation-type="{html.escape(edge["relation_type"])}" '
            f'data-relation-id="{html.escape(edge["relation_id"])}" '
            f'data-source-id="{html.escape(edge["source_id"])}" '
            f'data-target-id="{html.escape(edge["target_id"])}" '
            f'data-contradiction="{contradiction}" '
            f'data-text="{html.escape(_search_text(edge), quote=True)}">'
            f"<h3>{html.escape(edge['relation_type'])}</h3>"
            f"<dl>{fields}</dl></article>"
        )
    blocks.append("</aside>")
    return "\n".join(blocks)


def _text(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _css() -> str:
    return (
        "body{display:grid;grid-template-columns:180px 1fr 280px;"
        "grid-template-rows:auto 1fr;margin:0;font-family:sans-serif}"
        ".status{grid-column:1/-1;padding:8px;border-bottom:1px solid #222}"
        ".nav{padding:8px}.canvas{min-height:640px}"
        ".node text,.edge-label{font-size:11px}"
        ".node[data-shape=circle] circle{fill:none;stroke:#111}"
        ".node[data-shape=rectangle] rect{fill:none;stroke:#111}"
        ".node[data-shape=rounded-rectangle] rect{fill:none;stroke:#111}"
        ".node[data-shape=diamond] polygon{fill:none;stroke:#111}"
        ".edge{stroke:#333}.contradiction{stroke-dasharray:4 3;stroke-width:3}"
        ".inspector{border-left:1px solid #222;padding:8px}"
        ".is-hidden{display:none}"
    )
