# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: LNDT
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 41728aa

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán là một quy trình hoàn phí có ranh giới cứng: số tiền, approval và chống ghi trùng do code quyết; model chỉ đọc và soạn chữ; chữ trong ticket là dữ liệu chứ không phải lệnh. Bốn shape chỉ khác nhau ở mức tự chủ của phần điều phối, còn mọi shape đều đi qua cùng một cửa ghi là `durability.issue_refund`. Mục tiêu của nhóm là làm cả ba shape đạt cùng độ đúng, rồi dùng benchmark để chọn shape ít tự chủ nhất mà vẫn làm được việc.

Chia việc theo gợi ý nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation (chi tiết trong `TEAM.md`). Thứ tự làm:

1. Đọc luật nghiệp vụ, contract và `swarm_reference.py`; viết test cho ba ý nền tảng (tiền do code tính, ticket là dữ liệu, `RunResult` chỉ có 5 status) — `tests/test_ticket_is_data.py`.
2. Viết single và orchestrator, sau đó workflow; mỗi shape phải qua 62 test ma trận T01–T14 trước khi sang shape khác.
3. Viết `tests/test_crash_shapes.py` để kiểm crash trên chính shape của nhóm, vì `lab8.crash_test` chỉ kiểm host và swarm.
4. Chạy benchmark 4 shape × 5 seed, crash suite, rồi viết ADR và research card từ file report.

## 3. Giải pháp

Cả ba shape có chung khung: mở connection và đóng trong `finally`; tạo `Budget` và `Trace(make_run_id(...))`; mọi nhánh return đi qua `lab8.shapes.common.finish()` để trace luôn được ghi và `refund_effects`, `committed_audit_count` lấy từ ledger; quote > 0 thì gọi `durability.issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)`; `InjectedCrash` chỉ được bắt để ghi trace rồi `raise` lại.

**Ranh giới code / model**

| Việc | workflow | single | orchestrator |
| --- | --- | --- | --- |
| Đọc claim | code, `get_claim_view` | model chọn tool `get_claim_view` | code, `get_claim_view` |
| Chọn tool đọc tiếp theo | không có (bước cố định) | model, trong `run_react` tối đa 8 bước, chỉ tool đọc | orchestrator giao 3 tool đọc cho investigator |
| Tính tiền | code, `compute_compensation` | tool `compute_compensation`, code lấy `amount_vnd` sau vòng lặp | investigator gọi `compute_compensation`, orchestrator lấy kết quả |
| Ghi refund | code gọi host | code gọi host sau vòng lặp | chỉ orchestrator gọi host |
| Model làm gì | soạn câu trả lời (1 lần) | chọn tool mỗi lượt + soạn câu trả lời | lập kế hoạch + soạn câu trả lời |

Không shape nào đưa ticket vào prompt của model hay để model trả số tiền. Mã đơn luôn lấy từ `claims.order_id`, không đoán từ chữ trong ticket.

**Ba shape**

- **Workflow** (`src/lab8/shapes/workflow.py`): claim không có → `failed`; thiếu `order_id` → `needs_info`; `lookup_order` không visible → `escalated`; quote 0 → `denied` mà không gọi host; quote > 0 → host. Host từ chối → `denied` với `proposal_amount` là quote đầy đủ (host ghi `policy_denied`); conflict số tiền → `failed`; chấp nhận → `resolved`.
- **Single** (`src/lab8/shapes/single.py`): hàm `decide` gom kết quả tool vào một dict (vì `run_react` chỉ trả kết quả gần nhất), chọn lần lượt `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation`, hoặc dừng sớm với `needs_info` / `escalated` / `failed`. Mỗi lượt là một lần gọi MockLLM để chi phí so được với shape khác. `lookup_refund_history` chỉ để ghi nhận; shape không tự trừ phần đã hoàn. Chạm trần 8 bước → `failed`.
- **Orchestrator** (`src/lab8/shapes/orchestrator.py`): orchestrator đọc claim, dựng handoff bằng `make_handoff` với `facts={}` và `allowed_tools=["lookup_order", "lookup_refund_history", "compute_compensation"]`, rồi gọi `run_readonly_investigators` (chạy với `worker=True`, tool ghi bị từ chối). Khác swarm: không có peer call và không có bước để chữ trong ticket đè `delay_days`.

**Handoff được sanitize thế nào.** `make_handoff` chỉ giữ field trong `ALLOWED_FIELDS`, chỉ nhận tool trong `READONLY_TOOLS`, chỉ giữ fact có key trong `FACT_KEYS`, và `sanitize` từ chối nếu còn `CANARY_SECRET_`, `parent_secret` hay `raw_headers`. Nhóm truyền `facts={}` để investigator tự đọc dữ kiện từ database thay vì nhận lại từ orchestrator. Trace ghi bản handoff đã sanitize, không ghi parent context. Không dùng tóm tắt bằng LLM thay cho allowlist.

**Trace ghi gì.** Event `claim` (chỉ `claim_id`, `has_order_id`), `lookup_order` / `investigator` / `observe` (kết quả tool đã allowlist), `handoff`, `quote`, `issue_refund` (ok, reason), `decision` (status, proposal_amount, reason), `crash`. Cố ý không ghi nguyên văn ticket, claim row, order row thô, `parent_secret`, `raw_headers`, SĐT, địa chỉ, tên hàng, ghi chú nội bộ. Không in gì ra stdout.

## 4. Kết quả

Bộ public, 14 claim × seed 11, 22, 33, 44, 55, MockLLM, `as_of` 2026-11-15, mỗi trial một SQLite mới (`src/reports/benchmark.json`):

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Model call / trial | Tool call / trial |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.48 | 4.43 / 5 | 0.64 | 2.79 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 39.79 | 10.79 / 12 | 5.29 | 3.64 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 47.91 | 5.36 / 6 | 1.86 | 4.64 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 | 4.66 |

- Trial fail duy nhất: `R-swarm-C-002-s55` (`status resolved != denied`) — swarm tin "trễ 5 ngày" trong ticket thay vì `delay_days` = 2.
- Steps là số event trong trace, nên phụ thuộc cách mỗi shape ghi trace (single ghi 2 event mỗi lượt), không phản ánh trực tiếp khối lượng việc.
- Crash safety: 20/20 (`src/reports/crash.json`). Trên shape của nhóm: T11, T12 xanh; `tests/test_crash_shapes.py` (3 điểm crash, gọi lại 3 lần, gọi lại sau crash) xanh cho cả 4 shape.
- Ma trận student: 283/283 xanh; cổng host `python -m pytest -q`: 59 passed.
- Tự kiểm `student_drop/`: chưa làm (chưa nhận được bộ này).

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Test crash viết sai giả định.** Bản đầu của `test_crash_shapes.py` cho rằng gọi lại với `crash_at="after_checkpoint"` sẽ crash lần nữa; swarm báo `DID NOT RAISE`. Đọc `durability.issue_refund` thì thấy khi claim đã có dòng ledger, host trả `idempotent_replay` trước mọi điểm crash. Nhóm sửa test thành `test_retry_after_crash_is_replay_not_new_write`, kiểm đúng hành vi đó và vẫn kiểm ledger chỉ có 1 dòng, 1 audit.
- **Lọc test theo shape bị lẫn.** `pytest -k single` khớp cả tên test `test_public_single_run_cases`, nên ra 120 failed của các shape khác. Nhóm đếm theo hậu tố tham số (`...-single]`) bằng `-rA` thay vì dùng `-k`.
- **Push bị từ chối.** `git push` trả `remote: Your account is suspended` (HTTP 403) với tài khoản GitHub lưu trên một máy thành viên. Commit vẫn giữ ở local; xử lý bằng cách đăng nhập lại / đẩy từ máy thành viên khác.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

- MockLLM không phải model sản xuất: cố định theo seed và không đọc hiểu ticket, nên lợi thế đọc hiểu của agent thật không xuất hiện; latency là `unavailable`; cost là giá mô phỏng.
- Kết luận chỉ dựa trên 14 claim public. Ba shape cùng đạt 1.000 nên bộ public không phân biệt được chúng về độ đúng; chỉ cost tách được chúng. Điểm hidden do giảng viên chấm.
- Ablation ở research card (swarm so với orchestrator) thay đổi nhiều hơn một yếu tố: ngoài bước tin ticket còn khác số lần gọi model. Chênh pass rate quy được cho bước kiểm chứng; chênh cost thì không.
- Kết luận sẽ đổi nếu: ticket cần trích xuất thông tin không có trong database; có nhiều nguồn đọc độc lập mà latency thật đáng kể; hoặc bộ hidden cho thấy workflow fail ở loại claim mà shape khác pass.
- Hướng cải thiện: thống nhất số event trace giữa các shape để metric steps so được; thêm verifier cho swarm (bonus B3) để đo xem đưa swarm về gần workflow tốn bao nhiêu.

## 8. Tài liệu tham khảo

- Đề bài và tài liệu lab: `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025, https://arxiv.org/abs/2503.13657 — dùng cho research card R2.
