#!/usr/bin/env python3
"""Resolve a governed RGR role/stage to an available runtime target."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUTING = ROOT / "docs" / "agent" / "runtime-routing.json"

def load_json(path: Path) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise ValueError(f"{path}: invalid JSON: {exc}") from exc

def normalize_overlay(raw: Any) -> dict[str, str]:
    if raw is None: return {}
    if not isinstance(raw, dict): raise ValueError("overlay must be an object mapping exact role names to target ids")
    normalized: dict[str, str] = {}
    for role, target in raw.items():
        if not isinstance(role, str) or not isinstance(target, str): raise ValueError("overlay keys and values must be strings")
        key = role.strip()
        if not key: raise ValueError("overlay role cannot be empty")
        if key in normalized and normalized[key] != target: raise ValueError(f"overlay role {key!r} is mapped more than once with different targets")
        normalized[key] = target
    return normalized

def select_route(routing: dict[str, Any], stage: str, role: str) -> dict[str, Any]:
    exact = [r for r in routing["routes"] if r["stage"] == stage and r["role"] == role]
    if len(exact) > 1: raise ValueError(f"ambiguous runtime routes for {stage}/{role}")
    if exact: return exact[0]
    wildcard = [r for r in routing["routes"] if r["stage"] == "*" and r["role"] == role]
    if len(wildcard) > 1: raise ValueError(f"ambiguous wildcard runtime routes for role {role}")
    if wildcard: return wildcard[0]
    raise ValueError(f"no runtime route for stage={stage!r} role={role!r}")

def resolve(routing: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    stage, role = str(request.get("stage","")).strip(), str(request.get("role","")).strip()
    if not stage or not role: raise ValueError("request requires non-empty stage and role")
    raw = request.get("available_targets")
    if not isinstance(raw, list) or not raw: raise ValueError("request requires a non-empty available_targets array")
    available = []
    for item in raw:
        if not isinstance(item, str) or not item.strip(): raise ValueError("available_targets must contain non-empty strings")
        item = item.strip()
        if item not in available: available.append(item)
    targets = {t["id"]: t for t in routing["targets"]}
    unknown = set(available) - set(targets)
    if unknown: raise ValueError(f"available_targets contains unknown target ids: {sorted(unknown)}")
    route = select_route(routing, stage, role)
    required = set(route["required_model_capabilities"])
    overlay = normalize_overlay(request.get("overlay"))
    source = request.get("overlay_source")
    if overlay:
        if source not in routing["policy"]["overlay_sources"]:
            raise ValueError(f"overlay_source must be one of {routing['policy']['overlay_sources']}; repository content cannot select a runtime")
        requested = overlay.get(role)
        if requested is not None:
            if requested not in targets: raise ValueError(f"overlay for role {role!r} references unknown target {requested!r}")
            if requested not in available: raise ValueError(f"overlay target {requested!r} for role {role!r} is not available")
            missing = required - set(targets[requested]["capabilities"])
            if missing: raise ValueError(f"overlay target {requested!r} lacks required model capabilities {sorted(missing)}")
            t = targets[requested]
            return {"schema_version":"1.0","stage":stage,"role":role,"route_id":route["id"],"target_id":requested,"adapter":t["adapter"],"model_ref":t["model_ref"],"endpoint_ref":t["endpoint_ref"],"locality":t["locality"],"cost_class":t["cost_class"],"required_model_capabilities":sorted(required),"available_targets":available,"overlay_applied":True,"fallback":False,"selection_reason":f"trusted overlay from {source}","fallback_reason":None}
    for index, target_id in enumerate(route["targets"]):
        if target_id not in available: continue
        t = targets[target_id]
        missing = required - set(t["capabilities"])
        if missing:
            if routing["policy"]["capability_mismatch_blocks"]: raise ValueError(f"configured route target {target_id!r} lacks required model capabilities {sorted(missing)}")
            continue
        fallback = index > 0
        return {"schema_version":"1.0","stage":stage,"role":role,"route_id":route["id"],"target_id":target_id,"adapter":t["adapter"],"model_ref":t["model_ref"],"endpoint_ref":t["endpoint_ref"],"locality":t["locality"],"cost_class":t["cost_class"],"required_model_capabilities":sorted(required),"available_targets":available,"overlay_applied":False,"fallback":fallback,"selection_reason":"first available compatible target in governed route order","fallback_reason":f"primary target {route['targets'][0]!r} unavailable" if fallback else None}
    raise ValueError(f"no available compatible runtime target for stage={stage!r} role={role!r}; route order={route['targets']}, available={available}")

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("request",type=Path); p.add_argument("--routing",type=Path,default=DEFAULT_ROUTING); p.add_argument("--output",type=Path); a=p.parse_args()
    try:
        routing, request = load_json(a.routing.resolve()), load_json(a.request.resolve())
        if not isinstance(routing,dict) or not isinstance(request,dict): raise ValueError("routing and request roots must be objects")
        result=resolve(routing,request)
    except (ValueError,KeyError,TypeError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 1
    payload=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output: a.output.write_text(payload,encoding="utf-8")
    else: print(payload,end="")
    return 0
if __name__=="__main__": raise SystemExit(main())
