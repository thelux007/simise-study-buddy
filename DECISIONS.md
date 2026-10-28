# Decisions — thelux007/simise-study-buddy

Record date, decision, reason, tradeoff and consequences.

- GitHub is the source of truth. Each machine has its own clone.
- Context travels as reviewed files in the same repository as the project.
- Personal and company data use separate hubs and approved owners/access.
- 2026-10-28: Handover setup on its own branch `docs/handover-setup`, documentation only.
  Reason: keep main unchanged until the owner reviews. Tradeoff: Home PC must switch to
  that branch. Consequence: merge to main after the acceptance exercise.
- 2026-10-28: `server-data/` is git-ignored. Reason: it holds personal study data and the
  repository is public. Consequence: data does not move between devices through Git.
