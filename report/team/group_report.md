# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

- Phân công Shape B (`single` — Phạm Thị Hồng Ngọc): triển khai tác nhân đơn dùng vòng lặp ReAct giới hạn 8 bước, chỉ sử dụng tool đọc có cấu trúc và tách biệt hoàn toàn quyền tính tiền / ghi ledger về phía host.

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape B — `single` (Single ReAct agent)
- **Vòng lặp ReAct giới hạn:** sử dụng `lab8.runtime.run_react(conn, budget, observation={"claim_id": claim_id}, decide=decide, max_steps=8, worker=False)`. Mỗi lượt hàm `decide` gọi `mock_llm.complete(..., purpose="react", ...)` để đếm chi phí suy luận vào `Budget`, rồi chọn tuần tự 4 read tool: `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation`, gom kết quả qua closure `state` và dừng trước ngưỡng 8 bước.
- **Ranh giới code / model:** `decide` không bao giờ gọi `issue_refund` (bị `runtime.dispatch` chặn bởi `WRITE_TOOLS`), không đọc/tin các con số hay chỉ thị trong `ticket`, và không tự tính hay trừ tiền bồi thường. Sau vòng lặp, code của shape kiểm tra `stopped == "step_cap"` hoặc các nhánh thoát sớm (`failed`, `needs_info`, `escalated`), đọc `amount_vnd` do `compute_compensation` tính: nếu `<= 0` thì trả `denied` không gọi host; nếu `> 0` thì truyền **quote đầy đủ** và `crash_at` vào `durability.issue_refund` (chỉ bắt `InjectedCrash` để ghi sự kiện `crash` và `raise` lại).
- **Trace contract v1:** mọi nhánh trả về đều đi qua `done()` → `lab8.shapes.common.finish(...)`, ghi các event `claim` (`claim_id`, `has_order_id`), `lookup_order` (chỉ 7 field allowlist khi visible), `lookup_refund_history`, `quote`, `issue_refund`, `decision` và `crash`. Cố ý **không** ghi nguyên văn `ticket`, `parent_secret`, `raw_headers`, `phone`, `address`, `internal_note`, `item_name` vào trace hay stdout.

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
