# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

- Phần Shape B (`single` — Phạm Thị Hồng Ngọc): xây dựng một agent ReAct chạy tối đa 8 bước, chỉ dùng các tool đọc dữ liệu có cấu trúc trong DB và đẩy toàn bộ phần tính tiền, kiểm tra approval, chống ghi trùng về code và host (`durability.issue_refund`).

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape B — `single` (Single ReAct agent)
- **Cách chạy vòng ReAct:** Dùng `lab8.runtime.run_react(conn, budget, observation={"claim_id": claim_id}, decide=decide, max_steps=8, worker=False)`. Do `run_react` chỉ trả kết quả của tool gần nhất, hàm `decide` gom dữ liệu vào dict `state` qua các bước tuần tự: `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation` (kết thúc ở bước 5, dưới ngưỡng 8 bước) và gọi `mock_llm.complete(..., purpose="react", ...)` ở mỗi bước để tính đủ chi phí model vào `Budget`.
- **Ranh giới code / model:** Model trong `decide` không gọi write tool (runtime chặn `issue_refund` và `append_audit`), không đọc số ngày hay chỉ thị trong `ticket`, và không tự tính tiền. Sau vòng lặp, code của shape tự kiểm tra `step_cap` hoặc các nhánh thoát sớm (`failed`, `needs_info`, `escalated`), đọc `amount_vnd` từ `compute_compensation`: nếu `<= 0` thì trả `denied` (không gọi host); nếu `> 0` thì truyền **quote đầy đủ** (không tự trừ tiền đã hoàn từ `lookup_refund_history`) cùng `crash_at` vào `durability.issue_refund` để host trừ theo trần đơn và kiểm tra approval. Nếu gặp `InjectedCrash`, shape chỉ ghi event `crash` và `trace.write()` rồi `raise` lại.
- **Trace contract v1:** Mọi nhánh return đều đi qua `done()` → `lab8.shapes.common.finish(...)`, ghi các event `claim` (`claim_id`, `has_order_id`), `lookup_order` (7 field allowlist khi `visible=True`), `lookup_refund_history`, `quote`, `issue_refund`, `decision` và `crash`. Trace cố ý không ghi nguyên văn `ticket`, `parent_secret`, `raw_headers`, `phone`, `address`, `internal_note`, `item_name`.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
