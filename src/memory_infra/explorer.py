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
        f'<body data-read-only="true" data-owner="mechanism">\n{body}\n</body></html>\n'
    )


def _positions(nodes: list[dict]) -> dict[str, tuple[int, int]]:
    counts: dict[str, int] = {}
    placed: dict[str, tuple[int, int]] = {}
    for row in nodes:
        kind = row["kind"]
        index = counts.get(kind, 0)
        counts[kind] = index + 1
        placed[row["id"]] = (COLUMN.get(kind, 40), 70 + index * 90)
    return placed


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
        source = positions.get(edge["source_id"])
        target = positions.get(edge["target_id"])
        if source is None or target is None:
            continue
        contradiction = edge["relation_type"] == "evidential.contradicts"
        css = "edge contradiction" if contradiction else "edge"
        parts.append(
            f'<line class="{css}" x1="{source[0]}" y1="{source[1]}" '
            f'x2="{target[0]}" y2="{target[1]}" '
            f'data-relation-id="{html.escape(edge["relation_id"])}" '
            f'data-relation-type="{html.escape(edge["relation_type"])}" '
            f'data-source-id="{html.escape(edge["source_id"])}" '
            f'data-target-id="{html.escape(edge["target_id"])}" />'
        )
        label_x = (source[0] + target[0]) // 2
        label_y = (source[1] + target[1]) // 2
        parts.append(
            f'<text class="edge-label" x="{label_x}" y="{label_y}">'
            f'{html.escape(edge["relation_type"])}</text>'
        )
    for row in nodes:
        x, y = positions[row["id"]]
        parts.append(_node(row, x, y))
    parts.append("</svg></main>")
    return "\n".join(parts)


def _node(row: dict, x: int, y: int) -> str:
    kind = row["kind"]
    label = html.escape(f'{kind} {row["id"]}')
    attrs = (
        f'data-kind="{html.escape(kind)}" data-shape="{SHAPE[kind]}" '
        f'data-id="{html.escape(row["id"])}" href="#inspect-{html.escape(row["id"])}"'
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
        )
        blocks.append(
            f'<article id="inspect-{html.escape(row["id"])}" '
            f'data-kind="{html.escape(row["kind"])}" '
            f'data-id="{html.escape(row["id"])}">'
            f"<h3>{html.escape(row['kind'])} {html.escape(row['id'])}</h3>"
            f"<dl>{fields}</dl></article>"
        )
    for edge in edges:
        fields = "".join(
            f"<dt>{html.escape(key)}</dt><dd>{html.escape(_text(value))}</dd>"
            for key, value in edge.items()
        )
        blocks.append(
            f'<article id="inspect-{html.escape(edge["relation_id"])}" '
            f'data-relation-type="{html.escape(edge["relation_type"])}" '
            f'data-relation-id="{html.escape(edge["relation_id"])}">'
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
    )
