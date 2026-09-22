# Optional Honcho self-model integration

Agent Pretorius does not require Honcho. The local SQLite runtime preserves autobiographical memory, action history, relationships, agenda state, research notes, continuity probes, and explicit self-model claims without an external service.

Honcho is useful as an additional observational layer because Hermes can assign the Pretorius profile its own AI peer and allow that peer to observe its own messages. This can produce a second, independently maintained representation of recurring behavior. That representation should be treated as an inferred model, not canonical identity.

To enable it after the profile is working, run:

```bash
hermes -p agent-pretorius memory setup honcho
hermes -p agent-pretorius honcho peer --ai pretorius
hermes -p agent-pretorius honcho status
```

For character research, directional observation is the useful default because the AI peer can self-observe and also model its interactions. Keep the local Pretorius database as the authoritative experimental record even when Honcho is active.

Do not place a Honcho API key in this repository. Use the profile-local `.env` or the Hermes setup flow. A self-hosted Honcho instance is also supported by current Hermes releases.
