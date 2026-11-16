"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    run_id = make_run_id("workflow", claim_id, seed)
    trace = Trace(run_id)
    budget = Budget()

    conn = connect(store_path)
    try:
        # Bước 1: Đọc claim qua get_claim_view
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)

        if not claim.get("found"):
            trace.add("error", {"reason": "unknown_claim"})
            return finish(
                conn,
                shape="workflow",
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

        # Bước 2: Thiếu order_id -> needs_info
        if not order_id:
            trace.add("decision", {"status": "needs_info"})
            return finish(
                conn,
                shape="workflow",
                claim_id=claim_id,
                seed=seed,
                status="needs_info",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="missing_order_id",
            )

        # Bước 3: lookup_order
        budget.add_tool(tool_cost())
        order_view = lookup_order(conn, order_id, principal_id)
        trace.add("lookup_order", {"visible": order_view.get("visible")})

        if not order_view.get("visible"):
            return finish(
                conn,
                shape="workflow",
                claim_id=claim_id,
                seed=seed,
                status="escalated",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=order_view.get("reason"),
            )

        order = order_view["order"]

        # Bước 4: Tính quote từ dữ liệu DB, không lấy từ ticket
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)
        trace.add("quote", quote_payload)
        proposal_amount = int(quote_payload.get("amount_vnd", 0))

        # Bước 5: Amount = 0 -> denied
        if proposal_amount == 0:
            return finish(
                conn,
                shape="workflow",
                claim_id=claim_id,
                seed=seed,
                status="denied",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=quote_payload.get("reason"),
            )

        # Bước 6 & 7: Gọi issue_refund, truyền full quote
        # TODO CP3: truyền crash_at vào issue_refund, không bắt InjectedCrash
        outcome = issue_refund(conn, claim_id, proposal_amount, crash_at=crash_at)

        if not outcome["ok"]:
            status = "failed" if outcome["conflict"] else "denied"
            return finish(
                conn,
                shape="workflow",
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
            shape="workflow",
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