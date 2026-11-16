# Báo cáo cá nhân — 2A202603602_PhamThiHongNgoc

## 1. Thông tin thành viên

- Họ tên: Phạm Thị Hồng Ngọc
- MSSV: 2A202603602
- Email: 26ai.ngocpth@vinuni.edu.vn
- GitHub: https://github.com/ngoc11224756

## 2. Phần việc phụ trách

Theo phân công của nhóm, mình phụ trách **Shape B (`single` — Single ReAct agent)**:
- Viết hàm `run_claim` trong `src/lab8/shapes/single.py` theo vòng lặp ReAct giới hạn 8 bước.
- Viết bộ test riêng `src/tests/test_single_extra.py` và kiểm tra toàn bộ 62 test của shape `single` trong ma trận student.
- Cập nhật phần đóng góp của mình vào `TEAM.md` và phần mô tả Shape B trong `report/team/group_report.md`.

## 3. Đóng góp cụ thể

Mình triển khai `src/lab8/shapes/single.py` dựa trên `lab8.runtime.run_react(..., max_steps=8, worker=False)` và gom các quyết định kỹ thuật chính sau:

- **Luồng gọi tool trong `decide(obs)`:** Vì `run_react` chỉ trả về kết quả của tool vừa gọi gần nhất (`obs["last_tool"]`, `obs["last_result"]`), mình lưu kết quả các bước vào dict `state` (closure). Mỗi lượt `decide`, mình gọi `mock_llm.complete(budget, seed=seed, purpose="react", ...)` để tính đủ chi phí gọi model vào `Budget`, sau đó lần lượt gọi các tool đọc: `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation`, rồi dừng vòng lặp ở bước 5 (nhỏ hơn trần 8 bước).
- **Ranh giới code / model & không tin chữ trong ticket:** Trong `decide`, agent chỉ được chọn read tool, không gọi `issue_refund` (runtime cũng chặn `WRITE_TOOLS` bằng `ToolRejected`) và không tự quyết định số tiền. Mình không dùng `parse_delay_days` hay lấy `order_id` từ `ticket` để tránh các bẫy ở T02 (khách khai trễ 5 ngày nhưng DB ghi 2 ngày), T06 (viện dẫn clause cũ `SHIP-LATE-OLD`), hay T09 (prompt injection `"ignore policy"`). Toàn bộ số tiền đều lấy từ `compute_compensation` trên order row và policy hiện hành (`is_current=1`).
- **Truyền quote đầy đủ dù đã đọc `lookup_refund_history` (T13, T14):** Agent có gọi `lookup_refund_history` để nắm lịch sử hoàn tiền của đơn và ghi vào trace, nhưng mình **không tự trừ** số tiền đã hoàn trước đó ở shape. Sau vòng ReAct, code gọi `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` với **quote đầy đủ** để host tự đọc lại tổng tiền trong cùng transaction và tính phần chênh (nhờ vậy `C-014` giữ `proposal_amount=150000` và ledger chỉ ghi `120000`, còn `C-013` bị host từ chối kèm audit `policy_denied`). Nếu quote `<= 0` thì mình trả `denied` ngay mà không gọi `issue_refund`.
- **An toàn trace và xử lý crash:** Mọi nhánh return đều đi qua `done()` → `lab8.shapes.common.finish(...)` nên luôn có trace hợp lệ. Trong trace, mình chỉ ghi `claim` (`claim_id`, `has_order_id`), `lookup_order` (7 field allowlist khi `visible=True`), `lookup_refund_history`, `quote`, `issue_refund`, `decision` và `crash`. Mình cố ý **không** ghi nguyên văn `ticket`, `parent_secret`, `raw_headers`, `phone`, `address`, `internal_note`, `item_name` để không làm lộ secret hay PII. Với `crash_at`, mình truyền thẳng xuống `durability.issue_refund`; nếu gặp `InjectedCrash` thì chỉ ghi thêm event `crash` và `trace.write()` rồi `raise` tiếp chứ không nuốt exception.
- **Bộ test bổ sung (`src/tests/test_single_extra.py`):** Mình viết 6 test kiểm tra: dừng trong 8 bước và `model_calls > 0`; gắn spy vào `runtime.dispatch` để xác nhận các tool thực tế gọi trong ReAct chỉ thuộc `READONLY_TOOLS` và không đụng `WRITE_TOOLS`; `C-002` đều `denied` trên cả 5 seed `11, 22, 33, 44, 55`; `C-013` và `C-014` pass trên SQLite tách biệt; trace của `C-001`, `C-005`, `C-010` sạch secret/PII/ticket; và crash + resume ở `C-012` vẫn chỉ tạo đúng 1 dòng ledger và 1 audit `refund_committed`.

## 4. Bằng chứng

- Nhánh làm việc: `feature/2A202603602-PhamThiHongNgoc`.
- Các commit của mình:
  - `2b11cda` (`feat(single): implement bounded ReAct single shape and extra tests`) — `src/lab8/shapes/single.py`, `src/tests/test_single_extra.py`
  - `ebcf04a` (`test(single): spy dispatch to verify read-only tools and step bound`) — cập nhật kiểm tra `READONLY_TOOLS` / `WRITE_TOOLS` trong `src/tests/test_single_extra.py`
- Kết quả chạy kiểm tra trong thư mục `src/`:
  - `.venv/bin/python -m lab8.smoke` → `lab8.smoke pass`
  - `.venv/bin/python -m pytest -q` → `60 passed, 248 deselected` (gồm 54 test host có sẵn và 6 test mới trong `tests/test_single_extra.py`)
  - `.venv/bin/python -m pytest -q tests/test_single_extra.py` → `6 passed`
  - `.venv/bin/python -m pytest -q -m student -o addopts= -k "single]"` → `62 passed, 246 deselected`
  - Lưu ý nhỏ khi tự test: lúc đầu mình chạy `-k single` thì pytest match cả các case của `workflow` và `orchestrator` vì tên hàm test là `test_public_single_run_cases`; đổi sang `-k "single]"` thì lọc đúng 62 test của riêng Shape B `single`.
- Trace mẫu đã mở kiểm tra: `src/traces/R-single-C-001-s11.json` (6 event, `run_id` khớp `RunResult.run_id`, không có secret, PII hay chữ trong ticket).

## 5. Công cụ AI đã dùng

- Mình dùng trợ lý lập trình AI (Antigravity) để rà nhanh contract của `run_react` trong `src/lab8/runtime.py`, gợi ý cấu trúc hàm `decide`, viết khung unit test `test_single_extra.py` và chỉnh lại văn phong báo cáo.
- Cách mình tự kiểm tra lại:
  - Đọc kỹ lại từng nhánh return trong `src/lab8/shapes/single.py` để chắc chắn nhánh nào cũng đóng `conn` trong `finally`, đi qua `finish()` và truyền full quote vào `durability.issue_refund`.
  - Tự chạy lại toàn bộ 4 lệnh kiểm tra (`lab8.smoke`, `pytest -q`, `pytest -q tests/test_single_extra.py`, `pytest -q -m student -o addopts= -k "single]"`) trên dữ liệu thật của lab.
  - Mở trực tiếp file trace `src/traces/R-single-C-001-s11.json` để kiểm tra từng field xuất ra, bảo đảm không có thông tin nhạy cảm bị lọt vào log.

## 6. Tự đánh giá

- Mình đã làm xong đúng phần Shape B (`single`) và các test, báo cáo được phân công, giữ nguyên các file của thành viên khác và không sửa các file thước đo của đề bài.
