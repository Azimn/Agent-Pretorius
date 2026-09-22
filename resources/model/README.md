# Pretorius model and LoRA assets

Agent Pretorius can run now without a trained adapter because the Hermes identity, persistent state, character invariants, and archived behavioral corpus are independent of the current language-model substrate.

The archive contains LoRA training datasets but no trained Pretorius adapter weights or adapter configuration. During the 2026-09-22 consolidation, no `.safetensors`, `adapter_config.json`, GGUF adapter, or model card tied to the Pretorius LoRA was located.

If trained weights are recovered, preserve them with exact provenance: base model and revision, tokenizer, training dataset version, training code or command, rank and alpha, target modules, quantization assumptions, checksum, and evaluation notes.

Do not make adapter loading mandatory for Agent Pretorius continuity. It should be an experimental substrate condition. That lets the same persistent Pretorius be compared with no adapter, recovered LoRA, retrained LoRA, and different base models while keeping autobiographical state and identity evidence fixed.

Hermes itself can use any compatible local or OpenAI-compatible model endpoint. Adapter application therefore belongs at the inference-server layer when the selected server supports it, not inside the persistent identity database.
