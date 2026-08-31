# Team 2 — Spill Forensics & Vessel Attribution

> Team 2-specific implementation context.
> Read MASTER_CONTEXT.md before changing shared architecture or contracts.

## Person A — Hindcast Status

### Mission

Person A owns the reverse hindcast and probable source corridor generation.

```text
spill centroid + detection time
→ OpenDrift reverse hindcast
→ trajectory
→ buffered source corridor
→ Person B vessel matching