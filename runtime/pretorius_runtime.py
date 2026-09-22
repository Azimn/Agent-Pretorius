from __future__ import annotations

import argparse
import hashlib
import json
import random
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
DEFAULT_DB = Path("local/pretorius_state/pretorius.db")

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"

def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS memories (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, occurred_at TEXT NOT NULL,
 kind TEXT NOT NULL, summary TEXT NOT NULL, source TEXT NOT NULL,
 salience REAL NOT NULL, confidence REAL NOT NULL, tags_json TEXT NOT NULL,
 supersedes_id TEXT
);
CREATE TABLE IF NOT EXISTS self_model (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
 claim TEXT NOT NULL, evidence TEXT NOT NULL, confidence REAL NOT NULL,
 status TEXT NOT NULL, source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS relationships (
 peer_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, updated_at TEXT NOT NULL,
 summary TEXT NOT NULL, evidence_json TEXT NOT NULL,
 commitments_json TEXT NOT NULL, unresolved_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS actions (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, intention TEXT NOT NULL,
 action TEXT NOT NULL, outcome TEXT NOT NULL, source TEXT NOT NULL,
 success INTEGER, metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agenda (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
 title TEXT NOT NULL, description TEXT NOT NULL, priority INTEGER NOT NULL,
 status TEXT NOT NULL, source TEXT NOT NULL, tags_json TEXT NOT NULL,
 blocked_by TEXT, completed_at TEXT
);
CREATE TABLE IF NOT EXISTS pulses (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, mode TEXT NOT NULL,
 selected_agenda_id TEXT, note TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_notes (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
 kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
 confidence REAL NOT NULL, status TEXT NOT NULL, source TEXT NOT NULL,
 tags_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS trace_judgments (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, bundle_id TEXT NOT NULL,
 evaluator TEXT NOT NULL, judgment_json TEXT NOT NULL,
 frozen INTEGER NOT NULL DEFAULT 1, unblinded_at TEXT
);
CREATE TABLE IF NOT EXISTS continuity_runs (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, prompt_id TEXT NOT NULL,
 response TEXT NOT NULL, model_hint TEXT, metadata_json TEXT NOT NULL,
 response_sha256 TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_actions_created_at ON actions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agenda_status_priority ON agenda(status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_research_status ON research_notes(status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_continuity_prompt ON continuity_runs(prompt_id, created_at DESC);
"""

class Store:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))

    @staticmethod
    def decode(row: sqlite3.Row, json_fields: Iterable[str] = ()) -> dict[str, Any]:
        out = dict(row)
        for field in json_fields:
            if field in out:
                out[field[:-5]] = json.loads(out.pop(field))
        if "success" in out and out["success"] is not None:
            out["success"] = bool(out["success"])
        return out

    def add_memory(self, summary: str, source: str, kind: str = "episode",
                   salience: float = 0.5, confidence: float = 1.0,
                   tags: Iterable[str] = (), occurred_at: str | None = None,
                   supersedes_id: str | None = None) -> str:
        self.init()
        if not summary.strip() or not source.strip():
            raise ValueError("summary and source are required")
        rid = new_id("mem")
        now = utc_now()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO memories
                (id,created_at,occurred_at,kind,summary,source,salience,confidence,tags_json,supersedes_id)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (rid, now, occurred_at or now, kind, summary.strip(), source.strip(),
                 clamp01(salience), clamp01(confidence), json.dumps(sorted(set(tags))), supersedes_id),
            )
        return rid

    def recent_memories(self, limit: int = 12) -> list[dict[str, Any]]:
        self.init()
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM memories ORDER BY created_at DESC LIMIT ?", (max(0,limit),)).fetchall()
        return [self.decode(r, ("tags_json",)) for r in rows]

    def add_self_claim(self, claim: str, evidence: str, source: str,
                       confidence: float = 0.5, status: str = "active") -> str:
        self.init()
        rid, now = new_id("self"), utc_now()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO self_model
                (id,created_at,updated_at,claim,evidence,confidence,status,source)
                VALUES (?,?,?,?,?,?,?,?)""",
                (rid,now,now,claim.strip(),evidence.strip(),clamp01(confidence),status,source.strip()),
            )
        return rid

    def active_self_claims(self, limit: int = 20) -> list[dict[str, Any]]:
        self.init()
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM self_model WHERE status='active'
                ORDER BY confidence DESC, updated_at DESC LIMIT ?""", (max(0,limit),)
            ).fetchall()
        return [dict(r) for r in rows]

    def upsert_relationship(self, peer_id: str, display_name: str, summary: str,
                            evidence: Iterable[str] = (), commitments: Iterable[str] = (),
                            unresolved: Iterable[str] = ()) -> None:
        self.init()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO relationships
                (peer_id,display_name,updated_at,summary,evidence_json,commitments_json,unresolved_json)
                VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(peer_id) DO UPDATE SET
                display_name=excluded.display_name,updated_at=excluded.updated_at,
                summary=excluded.summary,evidence_json=excluded.evidence_json,
                commitments_json=excluded.commitments_json,unresolved_json=excluded.unresolved_json""",
                (peer_id.strip(),display_name.strip(),utc_now(),summary.strip(),
                 json.dumps(list(evidence)),json.dumps(list(commitments)),json.dumps(list(unresolved))),
            )

    def relationships(self) -> list[dict[str, Any]]:
        self.init()
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM relationships ORDER BY updated_at DESC").fetchall()
        return [self.decode(r, ("evidence_json","commitments_json","unresolved_json")) for r in rows]

    def log_action(self, intention: str, action: str, outcome: str, source: str,
                   success: bool | None = None, metadata: dict[str,Any] | None = None) -> str:
        self.init()
        rid = new_id("act")
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO actions
                (id,created_at,intention,action,outcome,source,success,metadata_json)
                VALUES (?,?,?,?,?,?,?,?)""",
                (rid,utc_now(),intention.strip(),action.strip(),outcome.strip(),source.strip(),
                 None if success is None else int(bool(success)),json.dumps(metadata or {},sort_keys=True)),
            )
        return rid

    def recent_actions(self, limit: int = 12) -> list[dict[str, Any]]:
        self.init()
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM actions ORDER BY created_at DESC LIMIT ?", (max(0,limit),)).fetchall()
        return [self.decode(r, ("metadata_json",)) for r in rows]

    def add_agenda(self, title: str, description: str, source: str, priority: int = 50,
                   tags: Iterable[str] = (), blocked_by: str | None = None) -> str:
        self.init()
        rid, now = new_id("task"), utc_now()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO agenda
                (id,created_at,updated_at,title,description,priority,status,source,tags_json,blocked_by,completed_at)
                VALUES (?,?,?,?,?,?,'open',?,?,?,NULL)""",
                (rid,now,now,title.strip(),description.strip(),int(priority),source.strip(),
                 json.dumps(sorted(set(tags))),blocked_by),
            )
        return rid

    def list_agenda(self, status: str = "open", limit: int = 50) -> list[dict[str, Any]]:
        self.init()
        query, args = "SELECT * FROM agenda", []
        if status != "all":
            query += " WHERE status=?"
            args.append(status)
        query += " ORDER BY priority DESC, created_at ASC LIMIT ?"
        args.append(max(0,limit))
        with self.connect() as conn:
            rows = conn.execute(query,args).fetchall()
        return [self.decode(r, ("tags_json",)) for r in rows]

    def complete_agenda(self, task_id: str, note: str | None = None) -> None:
        self.init()
        now = utc_now()
        with self.connect() as conn:
            if conn.execute("SELECT 1 FROM agenda WHERE id=?", (task_id,)).fetchone() is None:
                raise KeyError(task_id)
            conn.execute("UPDATE agenda SET status='done',updated_at=?,completed_at=? WHERE id=?", (now,now,task_id))
        if note:
            self.add_memory(note, f"agenda:{task_id}", "research", 0.7, 1.0, ("agenda","completion"))

    def add_research_note(self, kind: str, title: str, body: str, source: str,
                          confidence: float = 0.5, status: str = "open",
                          tags: Iterable[str] = ()) -> str:
        self.init()
        rid, now = new_id("note"), utc_now()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO research_notes
                (id,created_at,updated_at,kind,title,body,confidence,status,source,tags_json)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (rid,now,now,kind,title.strip(),body.strip(),clamp01(confidence),status,source.strip(),
                 json.dumps(sorted(set(tags)))),
            )
        return rid

    def research_notes(self, status: str = "open", limit: int = 20) -> list[dict[str, Any]]:
        self.init()
        query, args = "SELECT * FROM research_notes", []
        if status != "all":
            query += " WHERE status=?"
            args.append(status)
        query += " ORDER BY updated_at DESC LIMIT ?"
        args.append(max(0,limit))
        with self.connect() as conn:
            rows = conn.execute(query,args).fetchall()
        return [self.decode(r, ("tags_json",)) for r in rows]

    def pulse(self, mode: str = "research") -> dict[str, Any]:
        self.init()
        selected = next((x for x in self.list_agenda("open",20) if not x.get("blocked_by")), None)
        rid, note = new_id("pulse"), "No open unblocked agenda item."
        if selected:
            note = f"Selected: {selected['title']}"
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO pulses(id,created_at,mode,selected_agenda_id,note,metadata_json) VALUES (?,?,?,?,?,?)",
                (rid,utc_now(),mode,None if selected is None else selected["id"],note,"{}"),
            )
        return {
            "pulse_id":rid,"mode":mode,"selected":selected,
            "recent_memories":self.recent_memories(8),
            "recent_actions":self.recent_actions(8),
            "self_model":self.active_self_claims(10),
            "relationships":self.relationships(),
            "research_notes":self.research_notes("open",10),
        }

    def freeze_trace_judgment(self, bundle_id: str, evaluator: str, judgment: Any) -> str:
        self.init()
        rid = new_id("judge")
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO trace_judgments
                (id,created_at,bundle_id,evaluator,judgment_json,frozen)
                VALUES (?,?,?,?,?,1)""",
                (rid,utc_now(),bundle_id,evaluator,json.dumps(judgment,sort_keys=True)),
            )
        return rid

    def record_continuity(self, prompt_id: str, response: str, model_hint: str | None = None,
                          metadata: dict[str,Any] | None = None) -> str:
        self.init()
        rid = new_id("cont")
        digest = hashlib.sha256(response.encode("utf-8")).hexdigest()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO continuity_runs
                (id,created_at,prompt_id,response,model_hint,metadata_json,response_sha256)
                VALUES (?,?,?,?,?,?,?)""",
                (rid,utc_now(),prompt_id,response,model_hint,json.dumps(metadata or {},sort_keys=True),digest),
            )
        return rid

    def continuity_history(self, prompt_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        self.init()
        with self.connect() as conn:
            if prompt_id:
                rows = conn.execute(
                    "SELECT * FROM continuity_runs WHERE prompt_id=? ORDER BY created_at DESC LIMIT ?",
                    (prompt_id,max(0,limit)),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM continuity_runs ORDER BY created_at DESC LIMIT ?", (max(0,limit),)
                ).fetchall()
        return [self.decode(r, ("metadata_json",)) for r in rows]

FORBIDDEN_TRACE_KEYS = {
    "provenance","source","source_condition","condition","treatment","lesion",
    "expected","expected_label","score","branch","commit","ground_truth"
}

def build_blind_bundle(traces: list[dict[str,Any]], seed: int) -> tuple[dict[str,Any],dict[str,str]]:
    if len(traces) < 2:
        raise ValueError("At least two traces are required")
    shuffled = list(traces)
    random.Random(seed).shuffle(shuffled)
    visible, key = [], {}
    for i, trace in enumerate(shuffled):
        label = chr(ord("A")+i)
        context = dict(trace.get("context") or {})
        leak = FORBIDDEN_TRACE_KEYS.intersection(context)
        if leak:
            raise ValueError(f"Forbidden trace metadata: {', '.join(sorted(leak))}")
        visible.append({
            "label":label,
            "situation":str(trace["situation"]),
            "behavior":str(trace["behavior"]),
            "context":context,
        })
        key[label] = str(trace["source_id"])
    packet = {
        "schema_version":1,
        "bundle_id":new_id("bundle"),
        "instructions":"Evaluate behavioral congruence from the Agent Pretorius perspective. Several traces may be plausible and none is also allowed.",
        "traces":visible,
    }
    return packet,key

def seed_agenda(store: Store, seed_file: Path) -> dict[str,Any]:
    payload = json.loads(seed_file.read_text(encoding="utf-8"))
    existing = {x["title"] for x in store.list_agenda("all",1000)}
    added, skipped = [], []
    for item in payload.get("agenda",[]):
        if item["title"] in existing:
            skipped.append(item["title"])
            continue
        added.append(store.add_agenda(
            item["title"],item.get("description",""),item.get("source","seed"),
            int(item.get("priority",50)),item.get("tags",[]),item.get("blocked_by")
        ))
    return {"added":added,"skipped":skipped}

def choose_continuity_prompt(path: Path, seed: int | None = None) -> dict[str,Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    prompts = payload.get("prompts",payload)
    if not isinstance(prompts,list) or not prompts:
        raise ValueError("No prompts available")
    return random.Random(seed).choice(prompts)

def out(value: Any) -> None:
    print(json.dumps(value,indent=2,sort_keys=True,default=str))

def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser()
    p.add_argument("--db",type=Path,default=DEFAULT_DB)
    sp=p.add_subparsers(dest="cmd",required=True)
    sp.add_parser("init")
    x=sp.add_parser("remember"); x.add_argument("--summary",required=True); x.add_argument("--source",required=True); x.add_argument("--kind",default="episode"); x.add_argument("--salience",type=float,default=.5); x.add_argument("--confidence",type=float,default=1.0); x.add_argument("--tag",action="append",default=[])
    x=sp.add_parser("recent"); x.add_argument("--limit",type=int,default=12)
    x=sp.add_parser("self-claim"); x.add_argument("--claim",required=True); x.add_argument("--evidence",required=True); x.add_argument("--source",required=True); x.add_argument("--confidence",type=float,default=.5)
    x=sp.add_parser("action-log"); x.add_argument("--intention",required=True); x.add_argument("--action",required=True); x.add_argument("--outcome",required=True); x.add_argument("--source",required=True); x.add_argument("--success",choices=["true","false","unknown"],default="unknown")
    x=sp.add_parser("relationship-set"); x.add_argument("--peer-id",required=True); x.add_argument("--display-name",required=True); x.add_argument("--summary",required=True); x.add_argument("--evidence",action="append",default=[]); x.add_argument("--commitment",action="append",default=[]); x.add_argument("--unresolved",action="append",default=[])
    x=sp.add_parser("agenda-add"); x.add_argument("--title",required=True); x.add_argument("--description",default=""); x.add_argument("--source",required=True); x.add_argument("--priority",type=int,default=50); x.add_argument("--tag",action="append",default=[])
    x=sp.add_parser("agenda-list"); x.add_argument("--status",default="open"); x.add_argument("--limit",type=int,default=50)
    x=sp.add_parser("agenda-complete"); x.add_argument("task_id"); x.add_argument("--note")
    x=sp.add_parser("research-note"); x.add_argument("--kind",default="observation"); x.add_argument("--title",required=True); x.add_argument("--body",required=True); x.add_argument("--source",required=True); x.add_argument("--confidence",type=float,default=.5); x.add_argument("--status",default="open"); x.add_argument("--tag",action="append",default=[])
    x=sp.add_parser("research-list"); x.add_argument("--status",default="open"); x.add_argument("--limit",type=int,default=20)
    x=sp.add_parser("pulse"); x.add_argument("--mode",default="research")
    x=sp.add_parser("seed-agenda"); x.add_argument("seed_file",type=Path)
    x=sp.add_parser("trace-blind"); x.add_argument("input_file",type=Path); x.add_argument("output_dir",type=Path); x.add_argument("--seed",type=int,required=True)
    x=sp.add_parser("trace-freeze"); x.add_argument("bundle_id"); x.add_argument("judgment_file",type=Path); x.add_argument("--evaluator",default="agent-pretorius")
    x=sp.add_parser("continuity-prompt"); x.add_argument("prompt_file",type=Path); x.add_argument("--seed",type=int)
    x=sp.add_parser("continuity-record"); x.add_argument("prompt_id"); x.add_argument("response_file",type=Path); x.add_argument("--model-hint")
    x=sp.add_parser("continuity-history"); x.add_argument("--prompt-id"); x.add_argument("--limit",type=int,default=50)
    x=sp.add_parser("status"); x.add_argument("--compact",action="store_true")
    return p

def main(argv: list[str] | None = None) -> int:
    a=parser().parse_args(argv); s=Store(a.db)
    if a.cmd=="init": s.init(); out({"status":"ok","db":str(a.db),"schema_version":SCHEMA_VERSION})
    elif a.cmd=="remember": out({"status":"stored","id":s.add_memory(a.summary,a.source,a.kind,a.salience,a.confidence,a.tag)})
    elif a.cmd=="recent": out(s.recent_memories(a.limit))
    elif a.cmd=="self-claim": out({"status":"stored","id":s.add_self_claim(a.claim,a.evidence,a.source,a.confidence)})
    elif a.cmd=="action-log":
        success=None if a.success=="unknown" else a.success=="true"
        out({"status":"stored","id":s.log_action(a.intention,a.action,a.outcome,a.source,success)})
    elif a.cmd=="relationship-set": s.upsert_relationship(a.peer_id,a.display_name,a.summary,a.evidence,a.commitment,a.unresolved); out({"status":"stored","peer_id":a.peer_id})
    elif a.cmd=="agenda-add": out({"status":"stored","id":s.add_agenda(a.title,a.description,a.source,a.priority,a.tag)})
    elif a.cmd=="agenda-list": out(s.list_agenda(a.status,a.limit))
    elif a.cmd=="agenda-complete": s.complete_agenda(a.task_id,a.note); out({"status":"completed","id":a.task_id})
    elif a.cmd=="research-note": out({"status":"stored","id":s.add_research_note(a.kind,a.title,a.body,a.source,a.confidence,a.status,a.tag)})
    elif a.cmd=="research-list": out(s.research_notes(a.status,a.limit))
    elif a.cmd=="pulse": out(s.pulse(a.mode))
    elif a.cmd=="seed-agenda": out(seed_agenda(s,a.seed_file))
    elif a.cmd=="trace-blind":
        payload=json.loads(a.input_file.read_text(encoding="utf-8")); traces=payload.get("traces",payload)
        packet,key=build_blind_bundle(traces,a.seed); a.output_dir.mkdir(parents=True,exist_ok=True)
        pp=a.output_dir/"blind_packet.json"; kp=a.output_dir/"sealed_key.json"
        pp.write_text(json.dumps(packet,indent=2,sort_keys=True),encoding="utf-8")
        kp.write_text(json.dumps(key,indent=2,sort_keys=True),encoding="utf-8")
        out({"bundle_id":packet["bundle_id"],"blind_packet":str(pp),"sealed_key":str(kp)})
    elif a.cmd=="trace-freeze":
        judgment=json.loads(a.judgment_file.read_text(encoding="utf-8"))
        out({"status":"frozen","id":s.freeze_trace_judgment(a.bundle_id,a.evaluator,judgment)})
    elif a.cmd=="continuity-prompt": out(choose_continuity_prompt(a.prompt_file,a.seed))
    elif a.cmd=="continuity-record":
        response=a.response_file.read_text(encoding="utf-8")
        out({"status":"stored","id":s.record_continuity(a.prompt_id,response,a.model_hint)})
    elif a.cmd=="continuity-history": out(s.continuity_history(a.prompt_id,a.limit))
    elif a.cmd=="status":
        payload={
            "db":str(a.db),"agenda_open":s.list_agenda("open",20),
            "recent_memories":s.recent_memories(8),"recent_actions":s.recent_actions(8),
            "self_model":s.active_self_claims(10),"relationships":s.relationships(),
            "research_notes":s.research_notes("open",10),
        }
        if a.compact:
            payload={k:v for k,v in payload.items() if k=="db"}
            payload.update({
                "open_agenda_count":len(s.list_agenda("open",20)),
                "recent_memory_count":len(s.recent_memories(8)),
                "recent_action_count":len(s.recent_actions(8)),
                "active_self_claim_count":len(s.active_self_claims(10)),
                "relationship_count":len(s.relationships()),
                "open_research_note_count":len(s.research_notes("open",10)),
            })
        out(payload)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
