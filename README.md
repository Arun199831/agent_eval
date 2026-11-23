# agent_eval

A small LangChain refund agent, evaluated with seven DeepEval metrics. The point of the project is not the agent. It is learning which metrics can be trusted on an agent like this, and how to tell when a red score is the agent's fault and when it is the test's.

## The agent

A customer asks for a refund. The agent looks up what they bought, checks today's date, and refunds only the requested items that were bought within the last 30 days.

Tools: `get_user_purchase_history`, `get_today_date`, `calculate_right_refund`, `issue_refund_ticket`. Replies are returned as a structured `Answer`. The 30-day rule is enforced by the system prompt, not inside a tool (see Known limitations).

## Run it

```powershell
uv sync
copy .env.example .env      # then set OPENAI_API_KEY
uv run --env-file .env python evaluations/task_completions.py
```

There is one script per metric in `evaluations/`: `task_completions`, `tool_correctness`, `argument_correctness`, `answer_correctness`, `step_efficiency`, `plan_quality`, `plan_adherence`. Set the agent model in `agent/models.py` and the judge model in `evaluations/evaluations_models.py`.

Keep `AGENT_TODAY=2026-10-10` in your `.env`. The sample purchases are dated October, so with the real date every refund eventually falls outside the 30-day window and the goldens go stale.

## Results

Single runs with `AGENT_TODAY=2026-10-10`, mid-November 2026. Judged metrics vary between runs.

| Metric | Result | Verdict |
|---|---|---|
| Task completion | 7/7 after rewriting the rubric | Trusted |
| Tool correctness | 7/7 | Trusted, but compares tool names only |
| Answer correctness | 7/7 after fixing one golden | Trusted, only as good as the references |
| Argument correctness | 2/7 | Found one real bug, then penalised empty-argument calls |
| Step efficiency | 3/7 | Reasons contradicted each other |
| Plan quality | 0/7 | Scores a plan an LLM reconstructed from the trace |
| Plan adherence | 4/7 | Same problem as plan quality |

## What I found

- A task-completion rubric written as a checklist failed a correct answer. Rewriting it as mutually exclusive scenarios fixed it.
- The date tool had an unused `user` parameter that the model filled in on every call. Tool correctness scored 7/7 anyway, because it only compares names. Argument correctness caught it.
- Sample dates went stale as the calendar moved, so a correct agent started failing the goldens. Pinning the date fixed it.
- One golden claimed the username was "not valid", which no tool can know. The agent's wording was right and the golden was wrong.

## Windows note

Windows Application Control blocked newly released compiled packages. `pyproject.toml` pins `uuid-utils`, `jiter`, `ormsgpack` and `regex` to older releases. `scan_blocked.py` lists every blocked binary in one pass.

## Known limitations

- The 30-day rule lives in the prompt, so nothing in the trace proves it ran. Moving it into a tool would make it testable.
- If `AGENT_TODAY` is unset, the date tool silently falls back to the real date. For a test harness it should fail instead.
- Seven single-turn cases, one run each.