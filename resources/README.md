# Pretorius Resource Archive

This folder consolidates the Pretorius material currently available through the connected GitHub repositories and ChatGPT Library as of 2026-09-22.

The archive is intentionally broader than the active Agent Pretorius runtime. It preserves historical training data, persona artifacts, architecture references, and source snapshots so later work can distinguish inherited evidence from newly generated agent memory.

## Current contents

- `resources/architecture_extracts/Digital_Companion_System_Complete_Guide.txt`: 1 files
- `resources/architecture_extracts/Memory_System_Complete_Specification_v3_1.txt`: 1 files
- `resources/architecture_extracts/Persona_Framework_v3_1_Complete_Specification.txt`: 1 files
- `resources/architecture_extracts/Persona_Framework_v3_Technical_Spec.txt`: 1 files
- `resources/architecture_extracts/SCF_Reference.txt`: 1 files
- `resources/identity/Master_Persona_Framework_Pretorius.json`: 1 files
- `resources/identity/pretorius_character_invariants_v1.txt`: 1 files
- `resources/identity/pretorius_v0.2_graph.html`: 1 files
- `resources/legacy_prompts/Pretorius_Persona_Protocol_corrected.txt`: 1 files
- `resources/legacy_prompts/README.md`: 1 files
- `resources/lora/Pretorius_LoRA_Dataset_Canvas_v2.txt`: 1 files
- `resources/lora/pretorius_lora_dataset_v10_137_chat_records.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v11_162_chat_records.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v12_162_chat_records_voice_restored.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v13_180_chat_records.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v14_189_chat_records.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v15_199_chat_records.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v16_209_chat_records.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v17_271_chat_records.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v19_279_diversified_prompts.jsonl`: 1 files
- `resources/lora/pretorius_lora_dataset_v3_45_examples.txt`: 1 files
- `resources/lora/pretorius_lora_dataset_v4_65_examples.txt`: 1 files
- `resources/lora/pretorius_lora_dataset_v5_merged.txt`: 1 files
- `resources/lora/pretorius_lora_dataset_v6_136_records.txt`: 1 files
- `resources/lora/pretorius_lora_dataset_v7_136_records_voice_corrected.txt`: 1 files
- `resources/lora/pretorius_lora_dataset_v8_146_records.txt`: 1 files
- `resources/lora/pretorius_lora_dataset_v9_147_records.txt`: 1 files
- `resources/lora/pretorius_training_10_pairs.jsonl`: 1 files
- `resources/lora/pretorius_training_10_pairs.txt`: 1 files
- `resources/lora/pretorius_training_20_pairs.txt`: 1 files
- `resources/source_snapshots/Pretorius-Neural-Network`: 14 files
- `resources/source_snapshots/Pretorius-legacy`: 15 files

Total archived files before this manifest: 59.

## Important handling notes

`legacy_prompts/` is archival evidence only. It contains old role-play instructions that attempted to override safety constraints and should never be loaded as active Hermes or system instructions.

`lora/` preserves the dataset lineage rather than only the newest training set. That is deliberate, because changes between versions may explain later behavioral differences.

`source_snapshots/Pretorius-Neural-Network/` is a frozen text snapshot of the current main-line neural research repository. Blinded evaluations should not expose experimental condition provenance or hidden keys from live branches.

`source_snapshots/Pretorius-legacy/` contains selected cognition-relevant code from the older Pretorius application, especially identity, memory, autonomy, buddy/relationship, and task systems. It is implementation history, not character canon.

`architecture_extracts/` contains extracted-text archival copies of relevant PDF and DOCX files from the user's ChatGPT Library. The original binary files remain in the Library.

## Gaps found in the final search

No separate Pretorius LoRA adapter weights, `adapter_config.json`, safetensors file, or model card was located in the connected Library or Azimn GitHub search.

No file explicitly identifiable as the canonical Pretorius autobiography or developmental-history source was located.

No file explicitly identifiable as the previously referenced Persona Connectome was located.

No dataset named v18 was located. The available lineage jumps from v17 to v19.

If you have any of those locally, add them here rather than replacing the existing lineage.

## Full inventory

- `resources/architecture_extracts/Digital_Companion_System_Complete_Guide.txt`
- `resources/architecture_extracts/Memory_System_Complete_Specification_v3_1.txt`
- `resources/architecture_extracts/Persona_Framework_v3_1_Complete_Specification.txt`
- `resources/architecture_extracts/Persona_Framework_v3_Technical_Spec.txt`
- `resources/architecture_extracts/SCF_Reference.txt`
- `resources/identity/Master_Persona_Framework_Pretorius.json`
- `resources/identity/pretorius_character_invariants_v1.txt`
- `resources/identity/pretorius_v0.2_graph.html`
- `resources/legacy_prompts/Pretorius_Persona_Protocol_corrected.txt`
- `resources/legacy_prompts/README.md`
- `resources/lora/Pretorius_LoRA_Dataset_Canvas_v2.txt`
- `resources/lora/pretorius_lora_dataset_v10_137_chat_records.jsonl`
- `resources/lora/pretorius_lora_dataset_v11_162_chat_records.jsonl`
- `resources/lora/pretorius_lora_dataset_v12_162_chat_records_voice_restored.jsonl`
- `resources/lora/pretorius_lora_dataset_v13_180_chat_records.jsonl`
- `resources/lora/pretorius_lora_dataset_v14_189_chat_records.jsonl`
- `resources/lora/pretorius_lora_dataset_v15_199_chat_records.jsonl`
- `resources/lora/pretorius_lora_dataset_v16_209_chat_records.jsonl`
- `resources/lora/pretorius_lora_dataset_v17_271_chat_records.jsonl`
- `resources/lora/pretorius_lora_dataset_v19_279_diversified_prompts.jsonl`
- `resources/lora/pretorius_lora_dataset_v3_45_examples.txt`
- `resources/lora/pretorius_lora_dataset_v4_65_examples.txt`
- `resources/lora/pretorius_lora_dataset_v5_merged.txt`
- `resources/lora/pretorius_lora_dataset_v6_136_records.txt`
- `resources/lora/pretorius_lora_dataset_v7_136_records_voice_corrected.txt`
- `resources/lora/pretorius_lora_dataset_v8_146_records.txt`
- `resources/lora/pretorius_lora_dataset_v9_147_records.txt`
- `resources/lora/pretorius_training_10_pairs.jsonl`
- `resources/lora/pretorius_training_10_pairs.txt`
- `resources/lora/pretorius_training_20_pairs.txt`
- `resources/source_snapshots/Pretorius-Neural-Network/main/EXPERIMENT_LOG.md`
- `resources/source_snapshots/Pretorius-Neural-Network/main/EXPERIMENT_PROTOCOL.md`
- `resources/source_snapshots/Pretorius-Neural-Network/main/README.md`
- `resources/source_snapshots/Pretorius-Neural-Network/main/SEALED_TERMINAL.md`
- `resources/source_snapshots/Pretorius-Neural-Network/main/config/default.json`
- `resources/source_snapshots/Pretorius-Neural-Network/main/persona_net/__init__.py`
- `resources/source_snapshots/Pretorius-Neural-Network/main/persona_net/battery.py`
- `resources/source_snapshots/Pretorius-Neural-Network/main/persona_net/development.py`
- `resources/source_snapshots/Pretorius-Neural-Network/main/persona_net/encoding.py`
- `resources/source_snapshots/Pretorius-Neural-Network/main/persona_net/network.py`
- `resources/source_snapshots/Pretorius-Neural-Network/main/persona_net/phenotype_training.py`
- `resources/source_snapshots/Pretorius-Neural-Network/main/persona_net/probes.py`
- `resources/source_snapshots/Pretorius-Neural-Network/main/requirements.txt`
- `resources/source_snapshots/Pretorius-Neural-Network/main/resources/README.md`
- `resources/source_snapshots/Pretorius-legacy/main/CHANGELOG.md`
- `resources/source_snapshots/Pretorius-legacy/main/README.md`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/README.md`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/actions/agents.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/actions/autonomous.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/actions/identity.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/actions/tasks.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/app/api/buddy-memory/route.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/app/api/memory/scan/route.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/lib/agent-tasks.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/lib/autonomous-runner.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/lib/buddy-intelligence.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/lib/buddy-notify.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/lib/memory-retrieval.ts`
- `resources/source_snapshots/Pretorius-legacy/main/apps/web/src/lib/memory-scanner.ts`
