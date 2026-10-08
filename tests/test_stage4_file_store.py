"""Stage 4 file-store contract. Does not change V0.2 transitions."""

import copy
import hashlib
import hmac
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from memory_infra.store import (
    FileDurableStore,
    InMemoryDurableStore,
    MemoryService,
    SnapshotError,
    export_snapshot,
    _restart_capability,
)


def _service(store):
    return MemoryService(store=store, seed=7, context_budget=4, policy="none")


def _populate(service: MemoryService) -> None:
    observed = service.request("observe", {"content": "alpha fact", "source": "caller"})
    service.request("signal", {"name": "promote", "point_id": observed["point_id"], "reason": "useful"})
    event_id = next(iter(service.adapter._graph.events))
    service.request("signal", {"name": "open_thread", "event_id": event_id, "topic": "boundary"})
    service.request("signal", {"name": "decay", "target_id": event_id})


def test_missing_file_loads_as_empty(tmp_path):
    store = FileDurableStore(tmp_path / "missing.json")
    assert store.load_snapshot() is None


@pytest.mark.parametrize("payload", [b"", b"   ", b"{", b'{"version":1', b"\xff\xfe"])
def test_truncated_or_malformed_file_rejected(tmp_path, payload):
    path = tmp_path / "snap.json"
    path.write_bytes(payload)
    store = FileDurableStore(path, seal_key=b"restart-seal-key-32-bytes-long!!")
    with pytest.raises(SnapshotError):
        store.load_snapshot()


def test_incompatible_file_rejected(tmp_path):
    path = tmp_path / "snap.json"
    service = _service(FileDurableStore(path))
    _populate(service)
    service.save()
    raw = json.loads(path.read_text())
    raw["version"] = 99
    body = {key: raw[key] for key in raw if key not in {"integrity", "authenticity"}}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    raw["integrity"] = hashlib.sha256(canonical).hexdigest()
    path.write_text(json.dumps(raw))
    restarted = FileDurableStore(path, seal_key=_restart_capability(service.store))
    with pytest.raises(SnapshotError, match="incompatible"):
        restarted.load_snapshot()


def test_atomic_replace_keeps_previous_file_on_failure(tmp_path, monkeypatch):
    path = tmp_path / "snap.json"
    service = _service(FileDurableStore(path))
    _populate(service)
    service.save()
    previous = path.read_bytes()

    def _boom(src, dst):
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", _boom)
    service.request("observe", {"content": "should not land", "source": "caller"})
    with pytest.raises(OSError):
        service.save()
    assert path.read_bytes() == previous
    assert not list(tmp_path.glob(".snapshot-*"))


def test_same_snapshot_contract_on_memory_and_file(tmp_path):
    memory = _service(InMemoryDurableStore())
    _populate(memory)
    memory.save()
    memory_snapshot = memory.store.load_snapshot()
    file_store = FileDurableStore(tmp_path / "snap.json", seal_key=_restart_capability(memory.store))
    file_store.save_snapshot(memory_snapshot)
    loaded = file_store.load_snapshot()
    assert loaded == memory_snapshot
    other = _service(file_store)
    other.load()
    assert export_snapshot(other.adapter._graph)["trace"] == memory_snapshot["trace"]
    assert export_snapshot(other.adapter._graph)["states"] == memory_snapshot["states"]
    assert export_snapshot(other.adapter._graph)["relations"] == memory_snapshot["relations"]


def test_process_restart_round_trip(tmp_path):
    path = tmp_path / "snap.json"
    seal_path = tmp_path / "seal.bin"
    script = r"""
import os, sys
from pathlib import Path
from memory_infra.store import FileDurableStore, MemoryService, export_snapshot, _restart_capability
path, seal_path, mode = sys.argv[1:]
if mode == "save":
    service = MemoryService(store=FileDurableStore(path), seed=7, context_budget=4, policy="none")
    observed = service.request("observe", {"content": "alpha fact", "source": "caller"})
    service.request("signal", {"name": "promote", "point_id": observed["point_id"], "reason": "useful"})
    event_id = next(iter(service.adapter._graph.events))
    service.request("signal", {"name": "open_thread", "event_id": event_id, "topic": "boundary"})
    service.save()
    Path(seal_path).write_bytes(_restart_capability(service.store))
    snap = export_snapshot(service.adapter._graph)
    sys.stdout.write(snap["integrity"])
else:
    service = MemoryService(store=FileDurableStore(path, seal_key=Path(seal_path).read_bytes()), seed=7, context_budget=4, policy="none")
    service.load()
    snap = export_snapshot(service.adapter._graph)
    sys.stdout.write(snap["integrity"] + "\n" + str(len(snap["trace"])) + "\n" + str(len(snap["events"])) + "\n" + str(len(snap["relations"])))
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    saved = subprocess.run([sys.executable, "-c", script, str(path), str(seal_path), "save"], check=True, capture_output=True, text=True, env=env)
    loaded = subprocess.run([sys.executable, "-c", script, str(path), str(seal_path), "load"], check=True, capture_output=True, text=True, env=env)
    integrity, traces, events, relations = loaded.stdout.splitlines()
    assert integrity == saved.stdout
    assert int(traces) > 0
    assert int(events) > 0
    assert int(relations) >= 0
    # snapshot file itself does not contain the seal key
    assert seal_path.read_bytes().hex() not in path.read_text()


def test_file_store_rejects_recomputed_public_sha(tmp_path):
    path = tmp_path / "snap.json"
    service = _service(FileDurableStore(path))
    _populate(service)
    service.save()
    snapshot = json.loads(path.read_text())
    forged = copy.deepcopy(snapshot)
    forged["trace"] = list(forged["trace"]) + [{"reason": "caller-forged"}]
    body = {key: forged[key] for key in forged if key not in {"integrity", "authenticity"}}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    forged["integrity"] = hashlib.sha256(canonical).hexdigest()
    forged["authenticity"] = hmac.new(b"attacker-controlled-seal-key-32b!!", canonical, hashlib.sha256).hexdigest()
    path.write_text(json.dumps(forged))
    restarted = FileDurableStore(path, seal_key=_restart_capability(service.store))
    with pytest.raises(SnapshotError, match="authenticity"):
        restarted.load_snapshot()


def test_public_api_cannot_extract_seal_or_authorize_file_rewrite(tmp_path):
    """Caller surface is the package export and service/store methods only."""
    import memory_infra

    assert "restart_seal" not in memory_infra.__all__
    assert not hasattr(memory_infra, "restart_seal")
    path = tmp_path / "snap.json"
    store = FileDurableStore(path)
    service = _service(store)
    _populate(service)
    service.save()
    public_names = set(memory_infra.__all__) | set(dir(service)) | set(dir(store))
    assert "restart_seal" not in public_names
    assert "_restart_capability" not in memory_infra.__all__
    for obj in (service, store, service.adapter, service.adapter._graph):
        assert "seal" not in obj.__dict__
    raw = json.loads(path.read_text())
    assert "seal_key" not in raw
    forged = copy.deepcopy(raw)
    first_state = next(iter(forged["states"].values()))
    first_state["lifecycle_state"] = "latent" if first_state["lifecycle_state"] != "latent" else "active"
    body = {key: forged[key] for key in forged if key not in {"integrity", "authenticity"}}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    forged["integrity"] = hashlib.sha256(canonical).hexdigest()
    forged["authenticity"] = hmac.new(b"attacker-controlled-seal-key-32b!!", canonical, hashlib.sha256).hexdigest()
    path.write_text(json.dumps(forged))
    with pytest.raises(SnapshotError, match="authenticity"):
        store.load_snapshot()
    with pytest.raises(SnapshotError, match="authenticity"):
        service.request("load")
    with pytest.raises(SnapshotError):
        FileDurableStore(path).load_snapshot()
