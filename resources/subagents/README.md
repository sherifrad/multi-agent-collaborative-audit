# Solo-mode roster (Claude subagents)

Copy these into `.claude/agents/` (project) or `~/.claude/agents/` (user). Each file sets the role's safe default model;
the orchestrator overrides `model` per spawn using `python3 scripts/model_router.py route --role <role>`, which also
names the reasoning level to put in the brief. Every result from this roster is a same-model review: say so in the report.
`maca-referee` is not a subagent: the referee is `scripts/skill_ambassador_auditor.py`.
