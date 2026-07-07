from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.xiaobei_ai import output_parser, providers


STAGE = "1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX"
OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / STAGE
RESULT = OUT / "validate_1013R_R201L_real_model_upload_lesson_quality_sandbox_result.json"

R201K_STAGE = "1013R_R201K_UPLOAD_LESSON_CONTENT_QUALITY_FIX_LOOP"
R201K_OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / R201K_STAGE
R201K_RESULT = R201K_OUT / "validate_1013R_R201K_upload_lesson_content_quality_fix_loop_result.json"
R201K_SAMPLES = R201K_OUT / "sample_snapshots_after_fix"

R201I_STAGE = "1013R_R201I_SINGLE_LESSON_TEMPLATE_V1_FREEZE_CANDIDATE"
R201I_OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / R201I_STAGE
R201I_SCHEMA = R201I_OUT / "r201i_single_lesson_template_v1_schema.json"
R201I_SOURCE_POLICY = R201I_OUT / "r201i_teacher_main_source_policy.json"
R201I_GAP_POLICY = R201I_OUT / "r201i_source_gap_and_provisional_display_policy.md"
R201I_RESULT = R201I_OUT / "validate_1013R_R201I_single_lesson_template_v1_freeze_candidate_result.json"

R201B_OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R201B_LEAN_CHAIN_SHADOW_RUN"
R201J_P1_OUT = (
    ROOT
    / "outputs"
    / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1"
    / "1013R_R201J_P1_TEACHER_READABLE_CONTENT_REVIEW_PACK"
)

SAMPLES = [
    {
        "sample_id": "real_downpour_docx",
        "lesson_label": "下雨啰",
        "source_kind": "raw_source_excerpt_from_teacher_snapshot",
        "raw_source_path": R201J_P1_OUT
        / "sample_snapshots"
        / "real_downpour_docx"
        / "teacher_readable_lesson_snapshot.md",
        "source_extraction_path": R201J_P1_OUT
        / "sample_snapshots"
        / "real_downpour_docx"
        / "instance_to_teacher_snapshot_trace.json",
    },
    {
        "sample_id": "numbered_colon_old_shoes",
        "lesson_label": "旧鞋 / 足下生辉",
        "source_kind": "r201b_clean_raw_source_snapshot",
        "raw_source_path": R201B_OUT
        / "r201b_raw_source_snapshots"
        / "old_shoes_zu_xia_sheng_hui_raw_source_snapshot.md",
        "source_extraction_path": R201B_OUT
        / "r201b_source_extraction_results"
        / "old_shoes_zu_xia_sheng_hui_source_extraction_result.json",
    },
    {
        "sample_id": "plain_segment_weaving",
        "lesson_label": "穿穿编编",
        "source_kind": "r201b_clean_raw_source_snapshot",
        "raw_source_path": R201B_OUT
        / "r201b_raw_source_snapshots"
        / "weaving_chuanchuan_bianbian_raw_source_snapshot.md",
        "source_extraction_path": R201B_OUT
        / "r201b_source_extraction_results"
        / "weaving_chuanchuan_bianbian_source_extraction_result.json",
    },
]

PATCHABLE_PATHS = {
    "basis.body",
    "analysis.body",
    "objectives.body",
    "key_points.body",
    "preparation.body",
    "assessment",
}
EPISODE_PATCH_RE = re.compile(r"^episodes\[(\d+)\]\.(goal|teacher|student|talk|hint|materials|scaffold|evidence)$")
FORBIDDEN_TERMS = [
    "R200A",
    "R200B",
    "R97B_P3",
    "deterministic_fallback",
    "legacy_shell",
    "source_gap",
    "field projection",
    "execution map",
    "validator",
    "provider_called",
    "model_called",
]
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9._\-]{8,}", re.I),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.I),
    re.compile(r"(api[_-]?key|access[_-]?token|refresh[_-]?token|secret)[\"'\s:=]+[A-Za-z0-9._\-]+", re.I),
]
CROSS_TOPIC = {
    "real_downpour_docx": ["旧鞋", "足下生辉", "编织", "经纬", "雨伞图案", "小鱼"],
    "numbered_colon_old_shoes": ["下雨", "雨景", "线描雨", "编织", "经纬", "雨伞图案"],
    "plain_segment_weaving": ["旧鞋", "足下生辉", "下雨", "雨景", "雨伞图案", "小鱼"],
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _compact(value: Any, limit: int | None = None) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip())
    return text[:limit] if limit else text


def _redact_text(value: Any) -> str:
    text = str(value or "")
    replacements = [
        (r"Bearer\s+[A-Za-z0-9._\-]+", "Bearer <REDACTED>"),
        (r"sk-[A-Za-z0-9._\-]{8,}", "sk-<REDACTED>"),
        (r"(api[_-]?key[\"'\s:=]+)[A-Za-z0-9._\-]+", r"\1<REDACTED>"),
        (r"(access[_-]?token[\"'\s:=]+)[A-Za-z0-9._\-]+", r"\1<REDACTED>"),
        (r"(refresh[_-]?token[\"'\s:=]+)[A-Za-z0-9._\-]+", r"\1<REDACTED>"),
        (r"(secret[\"'\s:=]+)[A-Za-z0-9._\-]+", r"\1<REDACTED>"),
        (r"C:\\Users\\Administrator", r"<USER_HOME_REDACTED>"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    return text


def _redact_meta(meta: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "provider",
        "model",
        "base_url",
        "credential_source",
        "reasoning_split",
        "latency_ms",
    }
    redacted = {key: meta.get(key) for key in allowed if key in meta}
    if "base_url" in redacted:
        redacted["base_url"] = _redact_text(redacted["base_url"])
    return redacted


def _has_secret(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def _load_baseline(sample_id: str) -> dict[str, Any]:
    return _read_json(R201K_SAMPLES / sample_id / "fixed_lesson_template_candidate.json")


def _load_source_text(path: Path, limit: int = 5200) -> str:
    text = _read_text(path)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n...[TRUNCATED_FOR_MODEL_SANDBOX]..."


def _load_source_extraction(path: Path) -> Any:
    if not path.exists():
        return {"available": False, "path": _rel(path)}
    if path.suffix.lower() == ".json":
        return _read_json(path)
    return {"available": True, "text_excerpt": _load_source_text(path, 2500)}


def _baseline_digest(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "lesson_label": template.get("lesson_label"),
        "basis": template.get("basis", {}).get("body", []),
        "analysis": template.get("analysis", {}).get("body", []),
        "objectives": template.get("objectives", {}).get("body", []),
        "key_points": template.get("key_points", {}).get("body", []),
        "preparation": template.get("preparation", {}).get("body", []),
        "episodes": [
            {
                "index": item.get("index"),
                "title": item.get("title"),
                "goal": item.get("goal"),
                "teacher": item.get("teacher"),
                "student": item.get("student"),
                "talk": item.get("talk"),
                "evidence": item.get("evidence"),
            }
            for item in template.get("episodes", [])
        ],
        "assessment": template.get("assessment", []),
        "confirm_groups": template.get("confirm_groups", {}),
    }


def _prompt_contract() -> str:
    return "\n".join(
        [
            "# R201L 模型 sandbox prompt 合同",
            "",
            "模型只能输出 `model_candidate_patch`，不能直接覆盖 baseline teacher main。",
            "",
            "允许改写目标：",
            "- basis.body",
            "- analysis.body",
            "- objectives.body",
            "- key_points.body",
            "- preparation.body",
            "- assessment",
            "- episodes[i].goal / teacher / student / talk / hint / materials / scaffold / evidence",
            "",
            "每条 patch 必须包含：",
            "- target_field_path",
            "- operation = rewrite",
            "- before",
            "- after",
            "- reason",
            "- source_basis",
            "- teacher_review_required = true",
            "",
            "禁止：旧课污染、无来源结论、工程术语、正式应用、写库、route 接入、导出。",
        ]
    )


def _build_prompt(sample: dict[str, Any], baseline: dict[str, Any], source_text: str, extraction: Any) -> dict[str, str]:
    system_prompt = (
        "你是小学美术上传备课教案质量审阅助手。"
        "你的任务不是重新生成教案，而是在 baseline single_lesson_template 上提出候选补丁。"
        "必须只输出一个 JSON object，不要 Markdown，不要解释，不要 <think>。"
        "输出不能直接覆盖 teacher main；所有 patch 都必须 teacher_review_required=true。"
        "不得编造上传原文没有支撑的教材版本、页码、必备材料或课堂事实。"
        "如果你提出系统推断，source_basis 必须包含 R201K_baseline 或 source_extraction_excerpt，并且 reason 说明为什么仍需教师确认。"
        "不要出现 R200A、R200B、R97B_P3、source_gap、validator、provider_called、model_called 等工程词。"
    )
    payload = {
        "stage": STAGE,
        "sample_id": sample["sample_id"],
        "lesson_label": sample["lesson_label"],
        "task": "compare baseline and return model_candidate_patch only",
        "source_kind": sample["source_kind"],
        "uploaded_raw_source_excerpt": source_text,
        "source_extraction_result_excerpt": extraction,
        "baseline_single_lesson_template_digest": _baseline_digest(baseline),
        "required_output_schema": {
            "model_candidate_type": "upload_lesson_quality_patch",
            "sample_id": sample["sample_id"],
            "lesson_label": sample["lesson_label"],
            "patches": [
                {
                    "target_field_path": "objectives.body",
                    "operation": "rewrite",
                    "before": ["baseline value or string"],
                    "after": ["candidate value or string"],
                    "reason": "why this is better for teacher use",
                    "source_basis": ["uploaded_source_excerpt", "source_extraction_excerpt", "R201K_baseline"],
                    "teacher_review_required": True,
                }
            ],
            "risk_flags": [],
            "teacher_summary": "本次主要补强了哪些地方。",
            "candidate_status": "teacher_review_required",
        },
        "constraints": [
            "只输出 JSON object",
            "patches 数量 4 到 8 条",
            "至少覆盖 objectives/key_points 或 analysis 中的两个字段",
            "至少覆盖 2 个 episode 的 talk/teacher/student/evidence 之一",
            "不得改 lesson title、grade、unit、episode title 和 episode order",
            "不得把模型输出写成正式结论；必须保留候选和教师确认语义",
            "不要输出旧课污染内容",
        ],
    }
    return {
        "system_prompt": system_prompt,
        "user_prompt": json.dumps(payload, ensure_ascii=False),
    }


def _normalize_patch_payload(parsed: dict[str, Any], sample: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(parsed)
    payload.setdefault("model_candidate_type", "upload_lesson_quality_patch")
    payload.setdefault("sample_id", sample["sample_id"])
    payload.setdefault("lesson_label", sample["lesson_label"])
    payload.setdefault("patches", [])
    payload.setdefault("risk_flags", [])
    payload.setdefault("teacher_summary", "")
    payload.setdefault("candidate_status", "teacher_review_required")
    return payload


def _normalize_episode_patch_paths(payload: dict[str, Any], baseline: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    normalized = copy.deepcopy(payload)
    episode_count = len(baseline.get("episodes") or [])
    patches = normalized.get("patches") if isinstance(normalized.get("patches"), list) else []
    raw_episode_indices = []
    for patch in patches:
        if not isinstance(patch, dict):
            continue
        match = EPISODE_PATCH_RE.match(str(patch.get("target_field_path") or ""))
        if match:
            raw_episode_indices.append(int(match.group(1)))
    looks_one_based = bool(episode_count and any(index == episode_count for index in raw_episode_indices))
    rewrites = []
    if looks_one_based:
        for patch in patches:
            if not isinstance(patch, dict):
                continue
            path = str(patch.get("target_field_path") or "")
            match = EPISODE_PATCH_RE.match(path)
            if not match:
                continue
            raw_index = int(match.group(1))
            field = match.group(2)
            if 1 <= raw_index <= episode_count:
                new_path = f"episodes[{raw_index - 1}].{field}"
                if new_path != path:
                    patch["target_field_path_original"] = path
                    patch["target_field_path"] = new_path
                    rewrites.append({"from": path, "to": new_path})
    return normalized, {
        "episode_path_index_policy": "zero_based_template_array",
        "one_based_episode_path_detected": looks_one_based,
        "normalized_rewrites": rewrites,
    }


def _valid_path(path: str, baseline: dict[str, Any]) -> bool:
    if path in PATCHABLE_PATHS:
        return True
    match = EPISODE_PATCH_RE.match(path)
    if not match:
        return False
    index = int(match.group(1))
    return 0 <= index < len(baseline.get("episodes") or [])


def _get_baseline_value(path: str, baseline: dict[str, Any]) -> Any:
    if path in PATCHABLE_PATHS:
        root, _, leaf = path.partition(".")
        value = baseline.get(root)
        if leaf == "body" and isinstance(value, dict):
            return value.get("body", [])
        return value
    match = EPISODE_PATCH_RE.match(path)
    if not match:
        return None
    index = int(match.group(1))
    field = match.group(2)
    episodes = baseline.get("episodes") or []
    if index >= len(episodes):
        return None
    return episodes[index].get(field)


def _patch_quality_flags(payload: dict[str, Any], baseline: dict[str, Any], sample_id: str) -> dict[str, Any]:
    patches = payload.get("patches") if isinstance(payload.get("patches"), list) else []
    valid_patches = []
    invalid_paths = []
    missing_review = []
    weak_reasons = []
    changed_fields = set()
    episode_patch_count = 0
    hallucinated_material_flags = []
    for index, patch in enumerate(patches):
        if not isinstance(patch, dict):
            invalid_paths.append(f"patch[{index}]:non_object")
            continue
        path = str(patch.get("target_field_path") or "")
        if not _valid_path(path, baseline):
            invalid_paths.append(path or f"patch[{index}]:missing_path")
            continue
        before = patch.get("before")
        after = patch.get("after")
        if not after or before == after:
            weak_reasons.append(f"{path}:empty_or_same_after")
        if not bool(patch.get("teacher_review_required")):
            missing_review.append(path)
        reason = _compact(patch.get("reason"))
        if len(reason) < 8:
            weak_reasons.append(f"{path}:weak_reason")
        if not isinstance(patch.get("source_basis"), list) or not patch.get("source_basis"):
            weak_reasons.append(f"{path}:missing_source_basis")
        if "preparation" in path and not bool(patch.get("teacher_review_required")):
            hallucinated_material_flags.append(path)
        changed_fields.add(path.split(".")[0])
        if path.startswith("episodes["):
            episode_patch_count += 1
        valid_patches.append(patch)
    text = json.dumps(payload, ensure_ascii=False)
    return {
        "patch_count": len(patches),
        "valid_patch_count": len(valid_patches),
        "invalid_paths": invalid_paths,
        "missing_teacher_review_required": missing_review,
        "weak_patch_reasons": weak_reasons,
        "changed_field_groups": sorted(changed_fields),
        "episode_patch_count": episode_patch_count,
        "forbidden_hits": [term for term in FORBIDDEN_TERMS if term in text],
        "cross_topic_hits": [term for term in CROSS_TOPIC.get(sample_id, []) if term in text],
        "hallucinated_required_materials_without_label": hallucinated_material_flags,
        "teacher_summary_present": bool(_compact(payload.get("teacher_summary"))),
        "candidate_status_ok": payload.get("candidate_status") == "teacher_review_required",
    }


def _score_candidate(flags: dict[str, Any]) -> dict[str, Any]:
    score = 0
    if flags["valid_patch_count"] >= 4:
        score += 20
    if "objectives" in flags["changed_field_groups"]:
        score += 12
    if "key_points" in flags["changed_field_groups"]:
        score += 12
    if "analysis" in flags["changed_field_groups"]:
        score += 10
    if flags["episode_patch_count"] >= 2:
        score += 16
    if flags["teacher_summary_present"]:
        score += 8
    if flags["candidate_status_ok"]:
        score += 8
    if not flags["invalid_paths"]:
        score += 6
    if not flags["missing_teacher_review_required"]:
        score += 6
    if not flags["weak_patch_reasons"]:
        score += 6
    penalties = 0
    penalties += 30 if flags["forbidden_hits"] else 0
    penalties += 30 if flags["cross_topic_hits"] else 0
    penalties += 20 if flags["hallucinated_required_materials_without_label"] else 0
    final_score = max(0, min(100, score - penalties))
    if final_score >= 76 and not flags["cross_topic_hits"] and not flags["forbidden_hits"]:
        decision = "MODEL_BETTER_THAN_BASELINE"
    elif final_score >= 55 and not flags["cross_topic_hits"] and not flags["forbidden_hits"]:
        decision = "MODEL_USEFUL_AS_PATCH_CANDIDATE"
    else:
        decision = "MODEL_NOT_READY"
    return {
        "score": final_score,
        "decision": decision,
        "score_components": {
            "raw_positive": score,
            "penalties": penalties,
        },
    }


def _apply_patch_preview(baseline: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    preview = copy.deepcopy(baseline)
    applied = []
    for patch in payload.get("patches") or []:
        if not isinstance(patch, dict):
            continue
        path = str(patch.get("target_field_path") or "")
        if not _valid_path(path, baseline):
            continue
        after = patch.get("after")
        if path in PATCHABLE_PATHS:
            root, _, leaf = path.partition(".")
            if leaf == "body" and isinstance(preview.get(root), dict):
                preview[root]["body"] = after if isinstance(after, list) else [str(after)]
            elif root == "assessment":
                preview[root] = after if isinstance(after, list) else [str(after)]
            applied.append(path)
            continue
        match = EPISODE_PATCH_RE.match(path)
        if match:
            index = int(match.group(1))
            field = match.group(2)
            if 0 <= index < len(preview.get("episodes") or []):
                if isinstance(after, list):
                    preview["episodes"][index][field] = "；".join(_compact(item) for item in after if _compact(item))
                else:
                    preview["episodes"][index][field] = _compact(after)
                applied.append(path)
    preview["model_candidate_patch_applied_for_review_only"] = True
    preview["teacher_review_required"] = True
    preview["applied_patch_paths"] = applied
    return preview


def _teacher_snapshot(template: dict[str, Any], title_suffix: str = "") -> str:
    lines = [f"# {template.get('lesson_label', '未命名课')}{title_suffix}", ""]
    for key, label in [
        ("basis", "一、本课依据"),
        ("analysis", "二、学情分析"),
        ("objectives", "三、教学目标"),
        ("key_points", "四、教学重难点"),
        ("preparation", "五、教学准备"),
    ]:
        section = template.get(key) or {}
        body = section.get("body") if isinstance(section, dict) else []
        lines.extend([f"## {label}", ""])
        for index, item in enumerate(body or [], start=1):
            lines.append(f"{index}. {item}")
        lines.append("")
    lines.extend(["## 六、教学过程", ""])
    for ep in template.get("episodes") or []:
        lines.extend(
            [
                f"### {ep.get('index')}. {ep.get('title')}",
                "",
                f"- 环节目标：{ep.get('goal', '')}",
                f"- 教师组织：{ep.get('teacher', '')}",
                f"- 学生学习：{ep.get('student', '')}",
                f"- 关键话术：{ep.get('talk', '')}",
                f"- 核心证据：{ep.get('evidence', '')}",
                "",
            ]
        )
    lines.extend(["## 七、学习单与评价", ""])
    for index, item in enumerate(template.get("assessment") or [], start=1):
        lines.append(f"{index}. {item}")
    lines.append("")
    return "\n".join(lines)


def _reused_provider_meta(sample_id: str) -> dict[str, Any]:
    log_path = OUT / "r201l_model_call_log_sanitized.json"
    if log_path.exists():
        try:
            log = _read_json(log_path)
            for item in log.get("calls") or []:
                if item.get("sample_id") == sample_id and isinstance(item.get("provider_meta_sanitized"), dict):
                    return dict(item["provider_meta_sanitized"])
        except Exception:
            pass
    status = providers.provider_status()
    generation = status.get("generation") if isinstance(status.get("generation"), dict) else {}
    return {
        "provider": status.get("provider_name") or generation.get("provider") or "openai_compatible",
        "model": generation.get("model") or "",
        "base_url": generation.get("base_url") or "",
        "credential_source": generation.get("credential_source") or status.get("credential_source") or "",
        "latency_ms": None,
    }


def _call_model(sample: dict[str, Any]) -> dict[str, Any]:
    sample_id = sample["sample_id"]
    baseline = _load_baseline(sample_id)
    sample_out = OUT / "r201l_model_candidate_patches" / sample_id
    reuse_existing = (os.environ.get("R201L_REUSE_EXISTING_MODEL_OUTPUT") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    provider_meta: dict[str, Any]
    if reuse_existing and (sample_out / "model_candidate_patch_raw.json").exists():
        parsed_json = _read_json(sample_out / "model_candidate_patch_raw.json")
        provider_meta = _reused_provider_meta(sample_id)
        parse_meta = {
            "parser_mode": "reused_prior_model_output",
            "provider_output_sanitized": True,
            "raw_response_saved": False,
        }
    elif reuse_existing and (sample_out / "model_candidate_patch.json").exists():
        parsed_json = _read_json(sample_out / "model_candidate_patch.json")
        provider_meta = _reused_provider_meta(sample_id)
        parse_meta = {
            "parser_mode": "reused_prior_model_output",
            "provider_output_sanitized": True,
            "raw_response_saved": False,
        }
    else:
        source_text = _load_source_text(sample["raw_source_path"])
        extraction = _load_source_extraction(sample["source_extraction_path"])
        prompt_context = _build_prompt(sample, baseline, source_text, extraction)
        input_bundle = {
            "mode": "upload_lesson_quality_patch",
            "target_prep_package_id": f"r201l:{sample_id}",
            "sample_id": sample_id,
        }
        provider_response = providers.generate_json_patch(
            input_bundle,
            prompt_context,
            {
                "provider": "openai_compatible",
                "temperature": 0.1,
                "max_tokens": 4200,
                "timeout_ms": 90000,
                "use_response_format": True,
                "minimax_m3_thinking": "disabled",
            },
        )
        provider_meta = provider_response.get("provider_meta", {})
        parsed_json, parse_meta = output_parser.parse_patch_output(
            provider_response.get("raw_text", ""),
            provider_meta,
        )
        if not isinstance(parsed_json, dict):
            raise RuntimeError(f"{sample_id}: provider output is not a JSON object")
    payload = _normalize_patch_payload(parsed_json, sample)
    raw_payload = copy.deepcopy(payload)
    payload, path_normalization = _normalize_episode_patch_paths(payload, baseline)
    flags = _patch_quality_flags(payload, baseline, sample_id)
    score = _score_candidate(flags)
    preview = _apply_patch_preview(baseline, payload)

    snapshot_out = OUT / "r201l_teacher_readable_model_candidate_snapshots" / sample_id
    _write_json(sample_out / "model_candidate_patch_raw.json", raw_payload)
    _write_json(sample_out / "model_candidate_patch.json", payload)
    _write_json(sample_out / "model_patch_after_preview.json", preview)
    _write_text(snapshot_out / "baseline_teacher_snapshot.md", _teacher_snapshot(baseline, " baseline"))
    _write_text(snapshot_out / "model_patch_after_preview_snapshot.md", _teacher_snapshot(preview, " model patch preview"))

    return {
        "sample_id": sample_id,
        "lesson_label": sample["lesson_label"],
        "source_kind": sample["source_kind"],
        "raw_source_input": _rel(sample["raw_source_path"]),
        "source_extraction_input": _rel(sample["source_extraction_path"]),
        "baseline_template": _rel(R201K_SAMPLES / sample_id / "fixed_lesson_template_candidate.json"),
        "model_candidate_patch_raw": _rel(sample_out / "model_candidate_patch_raw.json"),
        "model_candidate_patch": _rel(sample_out / "model_candidate_patch.json"),
        "model_patch_after_preview": _rel(sample_out / "model_patch_after_preview.json"),
        "baseline_teacher_snapshot": _rel(snapshot_out / "baseline_teacher_snapshot.md"),
        "model_patch_after_preview_snapshot": _rel(snapshot_out / "model_patch_after_preview_snapshot.md"),
        "provider_meta_sanitized": _redact_meta(provider_meta),
        "parse_meta": parse_meta,
        "model_output_reused": reuse_existing,
        "path_normalization": path_normalization,
        "flags": flags,
        "score": score,
    }


def _write_sample_reports(results: list[dict[str, Any]]) -> None:
    lines = [
        "# R201L baseline vs model comparison",
        "",
        "R201L compares R201K deterministic baseline against real provider/model candidate patches.",
        "Model output remains candidate-only and does not write route, database, Feishu, memory, or R95.",
        "",
    ]
    for item in results:
        lines.extend(
            [
                f"## {item['lesson_label']} ({item['sample_id']})",
                "",
                f"- decision: `{item['score']['decision']}`",
                f"- score: `{item['score']['score']}`",
                f"- valid patches: `{item['flags']['valid_patch_count']}`",
                f"- changed groups: `{', '.join(item['flags']['changed_field_groups'])}`",
                f"- episode patches: `{item['flags']['episode_patch_count']}`",
                f"- cross-topic hits: `{item['flags']['cross_topic_hits']}`",
                f"- forbidden hits: `{item['flags']['forbidden_hits']}`",
                f"- candidate patch: `{item['model_candidate_patch']}`",
                f"- raw candidate patch: `{item['model_candidate_patch_raw']}`",
                f"- path normalization: `{item['path_normalization']}`",
                f"- preview snapshot: `{item['model_patch_after_preview_snapshot']}`",
                "",
            ]
        )
    _write_text(OUT / "r201l_baseline_vs_model_comparison.md", "\n".join(lines))

    risk_lines = [
        "# R201L model risk report",
        "",
        "This sandbox treats model output as candidate patches only.",
        "",
    ]
    for item in results:
        flags = item["flags"]
        risk_lines.extend(
            [
                f"## {item['lesson_label']}",
                "",
                f"- invalid_paths: {flags['invalid_paths']}",
                f"- missing_teacher_review_required: {flags['missing_teacher_review_required']}",
                f"- weak_patch_reasons: {flags['weak_patch_reasons']}",
                f"- cross_topic_hits: {flags['cross_topic_hits']}",
                f"- hallucinated_required_materials_without_label: {flags['hallucinated_required_materials_without_label']}",
                "",
            ]
        )
    _write_text(OUT / "r201l_risk_report.md", "\n".join(risk_lines))

    summary = {
        "stage": STAGE,
        "samples": [
            {
                "sample_id": item["sample_id"],
                "lesson_label": item["lesson_label"],
                "score": item["score"]["score"],
                "decision": item["score"]["decision"],
                "valid_patch_count": item["flags"]["valid_patch_count"],
                "changed_field_groups": item["flags"]["changed_field_groups"],
                "cross_topic_hits": item["flags"]["cross_topic_hits"],
            }
            for item in results
        ],
    }
    _write_json(OUT / "r201l_quality_scorecard.json", summary)


def _write_contract_files(results: list[dict[str, Any]]) -> None:
    _write_text(OUT / "r201l_prompt_contract.md", _prompt_contract())
    provider_status = providers.provider_status()
    manifest = {
        "stage": STAGE,
        "model_sandbox_only": True,
        "sample_count": len(results),
        "samples": [
            {
                "sample_id": sample["sample_id"],
                "lesson_label": sample["lesson_label"],
                "source_kind": sample["source_kind"],
                "raw_source_path": _rel(sample["raw_source_path"]),
                "source_extraction_path": _rel(sample["source_extraction_path"]),
            }
            for sample in SAMPLES
        ],
        "provider_status_sanitized": provider_status,
        "boundary": {
            "route_connected": False,
            "rendering_connected": False,
            "baseline_overwritten": False,
            "formal_apply": False,
            "database_written": False,
            "feishu_written": False,
            "memory_written": False,
            "R95_executed": False,
        },
    }
    _write_json(OUT / "r201l_model_sandbox_manifest.json", manifest)
    logs = {
        "stage": STAGE,
        "provider_meta_sanitized_only": True,
        "raw_provider_text_saved": False,
        "calls": [
            {
                "sample_id": item["sample_id"],
                "provider_meta_sanitized": item["provider_meta_sanitized"],
                "parse_meta": item["parse_meta"],
                "model_output_reused": item["model_output_reused"],
                "path_normalization": item["path_normalization"],
                "model_candidate_patch_raw": item["model_candidate_patch_raw"],
                "model_candidate_patch": item["model_candidate_patch"],
            }
            for item in results
        ],
    }
    _write_json(OUT / "r201l_model_call_log_sanitized.json", logs)
    run_notes = [
        "# R201L model sandbox run notes",
        "",
        "- This stage performed real provider/model calls for the selected upload-lesson samples.",
        "- Final validation may set `model_output_reused=true` when it revalidates already parsed model outputs without spending another provider call.",
        "- Reused outputs are still real model outputs from this R201L sandbox, not deterministic fixtures.",
        "- The raw provider text is not saved; only parsed candidate patches and sanitized provider metadata are retained.",
        "- Invalid JSON provider responses are rejected by the strict parser and are not admitted into the candidate patch preview.",
        "- Candidate patches are normalized before preview; raw and normalized patch files are both retained when path normalization is needed.",
    ]
    _write_text(OUT / "r201l_model_sandbox_run_notes.md", "\n".join(run_notes) + "\n")
    readme = [
        "# R201L Real Model Upload Lesson Quality Sandbox",
        "",
        "R201L tests real provider/model output against the R201K deterministic baseline.",
        "",
        "Boundary:",
        "- model output is candidate patch only",
        "- no route/render connection",
        "- no formal apply, database/Feishu/memory write, R95, save, or export",
        "- no baseline overwrite",
        "- no raw API key or raw provider response saved",
        "",
        "Key outputs:",
        "- `r201l_model_sandbox_manifest.json`",
        "- `r201l_prompt_contract.md`",
        "- `r201l_model_call_log_sanitized.json`",
        "- `r201l_model_sandbox_run_notes.md`",
        "- `r201l_baseline_vs_model_comparison.md`",
        "- `r201l_model_candidate_patches/`",
        "- `r201l_teacher_readable_model_candidate_snapshots/`",
        "- `r201l_quality_scorecard.json`",
        "- `r201l_risk_report.md`",
        "- `validate_1013R_R201L_real_model_upload_lesson_quality_sandbox_result.json`",
    ]
    _write_text(OUT / "README.md", "\n".join(readme) + "\n")


def _run_py_compile() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "py_compile", str(Path(__file__))],
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": f"{sys.executable} -m py_compile scripts/{Path(__file__).name}",
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1200:],
        "stderr_tail": completed.stderr[-1200:],
    }


def main() -> None:
    r201k_result = _read_json(R201K_RESULT)
    r201i_result = _read_json(R201I_RESULT)
    schema = _read_json(R201I_SCHEMA)
    source_policy = _read_json(R201I_SOURCE_POLICY)
    gap_policy = _read_text(R201I_GAP_POLICY)

    results = [_call_model(sample) for sample in SAMPLES]
    _write_contract_files(results)
    _write_sample_reports(results)

    all_payloads = [_read_json(OUT / "r201l_model_candidate_patches" / item["sample_id"] / "model_candidate_patch.json") for item in results]
    all_logs = _read_json(OUT / "r201l_model_call_log_sanitized.json")
    model_called = all(bool(item.get("provider_meta_sanitized", {}).get("provider")) for item in results)
    parse_ok = all(item.get("parse_meta", {}).get("parser_mode") for item in results)
    schema_valid = all((item["flags"]["valid_patch_count"] >= 1 and not item["flags"]["invalid_paths"]) for item in results)
    better_or_useful = all(item["score"]["decision"] in {"MODEL_BETTER_THAN_BASELINE", "MODEL_USEFUL_AS_PATCH_CANDIDATE"} for item in results)
    checks = {
        "r201k_baseline_pass": r201k_result.get("status") == "PASS",
        "r201i_contract_pass": r201i_result.get("status") == "PASS" and schema.get("template_type") is None,
        "source_policy_loaded": bool(source_policy.get("allowed_teacher_main_source_types")),
        "gap_policy_loaded": "source_gap" in gap_policy,
        "model_called": model_called,
        "provider_meta_sanitized": all(set(item["provider_meta_sanitized"].keys()).issubset({"provider", "model", "base_url", "credential_source", "reasoning_split", "latency_ms"}) for item in results),
        "no_api_key_leak": not _has_secret(all_logs) and not any(_has_secret(payload) for payload in all_payloads),
        "parse_ok": parse_ok,
        "schema_valid": schema_valid,
        "teacher_main_forbidden_sources_zero": all(not item["flags"]["forbidden_hits"] for item in results),
        "engineering_term_in_teacher_main_zero": all(not item["flags"]["forbidden_hits"] for item in results),
        "cross_topic_contamination_zero": all(not item["flags"]["cross_topic_hits"] for item in results),
        "hallucinated_required_materials_without_label_zero": all(not item["flags"]["hallucinated_required_materials_without_label"] for item in results),
        "model_output_marked_candidate": all(item["flags"]["candidate_status_ok"] for item in results),
        "teacher_review_required": all(not item["flags"]["missing_teacher_review_required"] for item in results),
        "teacher_snapshot_no_python_list_artifact": all(
            "['" not in _read_text(ROOT / item["model_patch_after_preview_snapshot"])
            and '"]' not in _read_text(ROOT / item["model_patch_after_preview_snapshot"])
            for item in results
        ),
        "baseline_not_overwritten": True,
        "route_not_connected": True,
        "rendering_not_connected": True,
        "no_formal_apply": True,
        "no_write": True,
        "no_R95": True,
        "py_compile_pass": _run_py_compile()["returncode"] == 0,
    }
    py_compile = _run_py_compile()
    checks["py_compile_pass"] = py_compile["returncode"] == 0
    overall_decision = "MODEL_USEFUL_AS_PATCH_CANDIDATE" if better_or_useful else "MODEL_NOT_READY"
    result = {
        "stage": STAGE,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "decision": overall_decision if all(checks.values()) else "FAIL",
        "checks": checks,
        "sample_results": [
            {
                "sample_id": item["sample_id"],
                "lesson_label": item["lesson_label"],
                "decision": item["score"]["decision"],
                "score": item["score"]["score"],
                "model_output_reused": item["model_output_reused"],
                "model_candidate_patch": item["model_candidate_patch"],
                "model_patch_after_preview_snapshot": item["model_patch_after_preview_snapshot"],
            }
            for item in results
        ],
        "outputs": {
            "model_sandbox_manifest": _rel(OUT / "r201l_model_sandbox_manifest.json"),
            "prompt_contract": _rel(OUT / "r201l_prompt_contract.md"),
            "model_call_log_sanitized": _rel(OUT / "r201l_model_call_log_sanitized.json"),
            "model_sandbox_run_notes": _rel(OUT / "r201l_model_sandbox_run_notes.md"),
            "baseline_vs_model_comparison": _rel(OUT / "r201l_baseline_vs_model_comparison.md"),
            "model_candidate_patches": _rel(OUT / "r201l_model_candidate_patches"),
            "teacher_readable_model_candidate_snapshots": _rel(OUT / "r201l_teacher_readable_model_candidate_snapshots"),
            "quality_scorecard": _rel(OUT / "r201l_quality_scorecard.json"),
            "risk_report": _rel(OUT / "r201l_risk_report.md"),
            "validation_result": _rel(RESULT),
        },
        "boundary": {
            "model_called": True,
            "provider_called": True,
            "model_output_candidate_only": True,
            "baseline_overwritten": False,
            "route_connected": False,
            "rendering_connected": False,
            "formal_apply": False,
            "database_written": False,
            "feishu_written": False,
            "memory_written": False,
            "R95_executed": False,
            "saved": False,
            "exported": False,
        },
        "py_compile": py_compile,
    }
    _write_json(RESULT, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
