# R201L model sandbox run notes

- This stage performed real provider/model calls for the selected upload-lesson samples.
- Final validation may set `model_output_reused=true` when it revalidates already parsed model outputs without spending another provider call.
- Reused outputs are still real model outputs from this R201L sandbox, not deterministic fixtures.
- The raw provider text is not saved; only parsed candidate patches and sanitized provider metadata are retained.
- Invalid JSON provider responses are rejected by the strict parser and are not admitted into the candidate patch preview.
- Candidate patches are normalized before preview; raw and normalized patch files are both retained when path normalization is needed.
