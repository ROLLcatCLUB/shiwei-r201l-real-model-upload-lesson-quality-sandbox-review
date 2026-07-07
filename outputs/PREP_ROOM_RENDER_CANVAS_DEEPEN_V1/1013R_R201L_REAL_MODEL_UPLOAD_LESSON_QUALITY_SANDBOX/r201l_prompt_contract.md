# R201L 模型 sandbox prompt 合同

模型只能输出 `model_candidate_patch`，不能直接覆盖 baseline teacher main。

允许改写目标：
- basis.body
- analysis.body
- objectives.body
- key_points.body
- preparation.body
- assessment
- episodes[i].goal / teacher / student / talk / hint / materials / scaffold / evidence

每条 patch 必须包含：
- target_field_path
- operation = rewrite
- before
- after
- reason
- source_basis
- teacher_review_required = true

禁止：旧课污染、无来源结论、工程术语、正式应用、写库、route 接入、导出。