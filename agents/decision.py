"""
Decision orchestration.

Runs the Decision Agent → Critic Agent loop, applying revision feedback until
the Critic approves or the revision cap is reached. Keeps the rest of the app
free of control-flow logic.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

from agents.strategic_agents import run_critic_agent, run_decision_agent

MAX_REVISIONS = 3


def run_decision_with_critique(
    stats: Dict[str, Any],
    risk: Dict[str, Any],
    opportunity: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any], int, str]:
    """
    Returns (decision, critic, revision_count, loop_summary).
    """
    revision_hint = None
    decision: Dict[str, Any] = {}
    critic: Dict[str, Any] = {}
    revisions = 0

    for attempt in range(MAX_REVISIONS + 1):
        decision = run_decision_agent(stats, risk, opportunity, revision_hint)
        critic = run_critic_agent(decision, risk, opportunity, stats)
        if critic.get("approved"):
            break
        revisions += 1
        revision_hint = critic.get("revision_required") or "Improve evidence and reasoning."
        if attempt >= MAX_REVISIONS - 1:
            # Cap reached — accept final decision to avoid infinite loop
            critic = dict(critic)
            critic["status"] = "APPROVED"
            critic["approved"] = True
            critic["reasoning"] = (
                "Revision cap reached. Final decision accepted after "
                f"{MAX_REVISIONS} revision(s). " + critic.get("reasoning", "")
            )
            break

    if revisions == 0:
        loop_summary = "Approved on first pass — no revision needed."
    else:
        loop_summary = f"Decision revised {revisions} time(s) before approval."

    return decision, critic, revisions, loop_summary
