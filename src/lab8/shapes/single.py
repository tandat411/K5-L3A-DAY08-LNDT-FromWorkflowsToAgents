"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete as llm_complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, lookup_refund_history, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)
    budget = Budget()

    conn = connect(store_path)
    try:
        # Đọc claim
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)

        if not claim.get("found"):
            trace.add("error", {"reason": "unknown_claim"})
            return finish(
                conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status="failed",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="unknown_claim",
            )

        order_id = claim.get("order_id")
        principal_id = claim["principal_id"]

        if not order_id:
            trace.add("decision", {"status": "needs_info"})
            return finish(
                conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status="needs_info",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="missing_order_id",
            )

        # Vòng ReAct — model chỉ dùng read tools
        def decide(state: dict) -> dict:
            # Model "quyết định" tool nào dùng tiếp theo
            # Với MockLLM: gọi llm_complete để tính budget, rồi chọn tool theo state
            last_tool = state.get("last_tool")
            if last_tool is None:
                # Bước đầu: lookup order
                llm_complete(budget, seed=seed, purpose="decide", prompt=str(state))
                return {"tool": "lookup_order", "args": {"order_id": order_id, "principal_id": principal_id}}
            if last_tool == "lookup_order":
                llm_complete(budget, seed=seed, purpose="decide", prompt=str(state))
                return {"final": state.get("last_result", {})}
            # Fallback: kết thúc
            return {"final": state.get("last_result", {})}

        result = run_react(
            conn,
            budget,
            observation={"claim": claim},
            decide=decide,
            max_steps=8,
            worker=False,
        )

        trace.add("react_result", {"stopped": result.get("stopped")})

        # Lấy dữ liệu order từ lịch sử tool calls, KHÔNG từ model output
        order_view = None
        final = result.get("final", {})
        obs = result.get("observation", {})

        # Tìm order_view trong observation hoặc final
        if obs.get("last_tool") == "lookup_order":
            order_view = obs.get("last_result")
        elif isinstance(final, dict) and final.get("visible") is not None:
            order_view = final

        if order_view is None or not order_view.get("visible"):
            reason = (order_view or {}).get("reason", "escalated")
            trace.add("decision", {"status": "escalated", "reason": reason})
            return finish(
                conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status="escalated",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=reason,
            )

        order = order_view["order"]

        # Tính quote từ dữ liệu DB
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)
        trace.add("quote", quote_payload)
        proposal_amount = int(quote_payload.get("amount_vnd", 0))

        if proposal_amount == 0:
            return finish(
                conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status="denied",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=quote_payload.get("reason"),
            )

        # TODO CP3: truyền crash_at vào issue_refund, không bắt InjectedCrash
        outcome = issue_refund(conn, claim_id, proposal_amount, crash_at=crash_at)

        if not outcome["ok"]:
            status = "failed" if outcome["conflict"] else "denied"
            return finish(
                conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status=status,
                proposal_amount=proposal_amount,
                budget=budget,
                trace=trace,
                error_reason=outcome["reason"],
            )

        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="resolved",
            proposal_amount=proposal_amount,
            budget=budget,
            trace=trace,
            error_reason=None,
        )
    finally:
        conn.close()