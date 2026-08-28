# Change Request Process

## When you need one

- The change touches files you do not own (`OWNERSHIP_MATRIX.md`)
- The change modifies an interface in `INTERFACE_CONTRACTS.md`
- The change alters project strategy, methodology, or the research roadmap
- The change touches a shared file (`configs/base.yaml`, `requirements.txt`, ...)
- You want to re-test something listed under "Rejected approaches" in `TEAM_SOT.md`

## When you don't

Anything entirely inside your own directories that keeps your published interfaces
intact. That is most work, by design.

## Process

1. Copy `change_requests/TEMPLATE.md` to
   `change_requests/CR-NNNN-short-slug.md`.
2. Fill it in. Open a PR containing **only** the change request file.
3. Tag the affected owners plus Min.
4. On approval, implement it in a follow-up PR that links the CR.
5. Update `INTERFACE_CONTRACTS.md` and `TEAM_SOT.md` in that same follow-up PR.
6. Set the CR status to `IMPLEMENTED`.

Approval rule: **every affected owner + Min**. Min alone cannot approve a change to
someone else's interface.

## Statuses

```text
PROPOSED · UNDER REVIEW · APPROVED · REJECTED · IMPLEMENTED · WITHDRAWN
```

Rejected CRs stay in the repository. A rejected proposal is evidence of a considered
alternative and is worth as much as an accepted one at review time.

## Emergency exception

If `main` is broken and the fix crosses a boundary, fix it, then file a retrospective CR
within 24 hours marked `EMERGENCY`. This should be rare enough to be memorable.
