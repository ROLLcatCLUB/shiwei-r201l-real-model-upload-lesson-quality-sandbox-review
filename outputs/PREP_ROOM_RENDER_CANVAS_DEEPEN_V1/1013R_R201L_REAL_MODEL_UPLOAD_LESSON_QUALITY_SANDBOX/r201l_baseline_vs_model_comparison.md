# R201L baseline vs model comparison

R201L compares R201K deterministic baseline against real provider/model candidate patches.
Model output remains candidate-only and does not write route, database, Feishu, memory, or R95.

## 下雨啰 (real_downpour_docx)

- decision: `MODEL_BETTER_THAN_BASELINE`
- score: `94`
- valid patches: `8`
- changed groups: `episodes[1], episodes[2], episodes[4], episodes[5], key_points, objectives`
- episode patches: `6`
- cross-topic hits: `[]`
- forbidden hits: `[]`
- candidate patch: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_model_candidate_patches/real_downpour_docx/model_candidate_patch.json`
- raw candidate patch: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_model_candidate_patches/real_downpour_docx/model_candidate_patch_raw.json`
- path normalization: `{'episode_path_index_policy': 'zero_based_template_array', 'one_based_episode_path_detected': True, 'normalized_rewrites': [{'from': 'episodes[2].teacher', 'to': 'episodes[1].teacher'}, {'from': 'episodes[2].evidence', 'to': 'episodes[1].evidence'}, {'from': 'episodes[3].teacher', 'to': 'episodes[2].teacher'}, {'from': 'episodes[5].teacher', 'to': 'episodes[4].teacher'}, {'from': 'episodes[6].talk', 'to': 'episodes[5].talk'}, {'from': 'episodes[6].evidence', 'to': 'episodes[5].evidence'}]}`
- preview snapshot: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_teacher_readable_model_candidate_snapshots/real_downpour_docx/model_patch_after_preview_snapshot.md`

## 旧鞋 / 足下生辉 (numbered_colon_old_shoes)

- decision: `MODEL_BETTER_THAN_BASELINE`
- score: `100`
- valid patches: `8`
- changed groups: `analysis, episodes[0], episodes[1], episodes[2], episodes[3], episodes[4], key_points, objectives`
- episode patches: `5`
- cross-topic hits: `[]`
- forbidden hits: `[]`
- candidate patch: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_model_candidate_patches/numbered_colon_old_shoes/model_candidate_patch.json`
- raw candidate patch: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_model_candidate_patches/numbered_colon_old_shoes/model_candidate_patch_raw.json`
- path normalization: `{'episode_path_index_policy': 'zero_based_template_array', 'one_based_episode_path_detected': False, 'normalized_rewrites': []}`
- preview snapshot: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_teacher_readable_model_candidate_snapshots/numbered_colon_old_shoes/model_patch_after_preview_snapshot.md`

## 穿穿编编 (plain_segment_weaving)

- decision: `MODEL_BETTER_THAN_BASELINE`
- score: `94`
- valid patches: `8`
- changed groups: `episodes[0], episodes[1], episodes[4], key_points, objectives, preparation`
- episode patches: `5`
- cross-topic hits: `[]`
- forbidden hits: `[]`
- candidate patch: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_model_candidate_patches/plain_segment_weaving/model_candidate_patch.json`
- raw candidate patch: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_model_candidate_patches/plain_segment_weaving/model_candidate_patch_raw.json`
- path normalization: `{'episode_path_index_policy': 'zero_based_template_array', 'one_based_episode_path_detected': False, 'normalized_rewrites': []}`
- preview snapshot: `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R201L_REAL_MODEL_UPLOAD_LESSON_QUALITY_SANDBOX/r201l_teacher_readable_model_candidate_snapshots/plain_segment_weaving/model_patch_after_preview_snapshot.md`
