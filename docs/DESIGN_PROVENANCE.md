# Design provenance

Agent Pretorius deliberately combines several architecture patterns rather than treating any one framework as sufficient.

Hermes Agent profiles provide the execution boundary. A profile isolates configuration, memory, sessions, skills, cron state, and the global `SOUL.md`. Hermes Bot Mode also supports durable named profiles and agent-to-agent messaging.

Hermes documentation:
https://hermes-agent.nousresearch.com/docs/user-guide/profiles
https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode
https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files

The Hyakkano project demonstrates separate Hermes gateway processes for distinct characters with independent runtime profiles and memories:
https://github.com/hafizhrf/hyakkano

Honcho contributes the useful peer model: memory can represent users, agents, NPCs, groups, and relationships rather than only a user profile. Its reasoning and dreaming model motivates our distinction between raw experiences and revisable conclusions:
https://honcho.dev/
https://honcho.dev/blog/blog/common-patterns-for-building-with-honcho

MemGPT contributes hierarchical memory management and the principle that long-term continuity should not depend on fitting the whole history into the active context:
https://arxiv.org/abs/2310.08560

Generative Agents contributes the memory, reflection, and planning pattern for believable persistent behavior:
https://arxiv.org/abs/2304.03442

Agent Pretorius keeps these ideas auditable. Canon, memories, relationships, self-model claims, research notes, and action outcomes remain inspectable data rather than opaque prompt text.
