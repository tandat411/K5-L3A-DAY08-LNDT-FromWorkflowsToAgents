# Báo cáo cá nhân — 2A202603602_PhamThiHongNgoc

## 1. Thông tin thành viên

- Họ tên: Phạm Thị Hồng Ngọc
- MSSV: 2A202603602
- Email: 
- GitHub: https://github.com/ngoc11224756

## 2. Phần việc phụ trách

- Thiết kế và triển khai **Shape B (`single` — Single ReAct agent)** tại `src/lab8/shapes/single.py`.
- Viết bộ kiểm thử riêng cho Shape B tại `src/tests/test_single_extra.py`.


## 3. Đóng góp cụ thể

- Cài đặt `run_claim` trong `src/lab8/shapes/single.py` sử dụng `lab8.runtime.run_react(..., max_steps=8, worker=False)` với hàm `decide` ghi nhận lượt suy luận của MockLLM (`complete(..., purpose="react", ...)`), gom kết quả các tool đọc qua closure `state`, gọi tuần tự: `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation`.
- Bảo đảm ranh giới code / model:
  - `decide` tuyệt đối không gọi `issue_refund`, không tin số ngày trễ hay chỉ thị trong `ticket`, và không tự quyết định số tiền.
  - Sau vòng lặp `run_react`, code của shape kiểm tra `stopped == "step_cap"` hoặc trạng thái kết thúc sớm (`failed`, `needs_info`, `escalated`), đọc `amount_vnd` từ `compute_compensation` (do code tính), từ chối ngay khi quote = 0 (không gọi `issue_refund`), và truyền **quote đầy đủ** cùng `crash_at` vào `durability.issue_refund` khi quote > 0 (bắt `InjectedCrash` chỉ để ghi `crash` vào trace và `raise` lại).
- Bảo đảm Trace contract v1 sạch secret/PII: ghi các event `claim` (chỉ `claim_id`, `has_order_id`), `lookup_order` (chỉ 7 field allowlist khi visible), `lookup_refund_history`, `quote`, `issue_refund`, `decision` và `crash`; tuyệt đối không ghi nguyên văn `ticket`, `parent_secret`, `raw_headers`, SĐT, địa chỉ, tên hàng hay ghi chú nội bộ.
- Viết 6 unit test trong `src/tests/test_single_extra.py`: kiểm tra dừng ≤ 8 bước và `model_calls > 0`, kiểm tra không cho phép gọi write tool trong runtime và không ghi ledger khi quote = 0, bỏ qua số ngày nói dối trong ticket trên cả 5 seed (`11, 22, 33, 44, 55`), truyền quote đầy đủ cho `T13`/`T14`, trace sạch secret/PII/ticket, và lan truyền + resume an toàn khi crash ở `C-012`.

## 4. Bằng chứng

- Commit chính & code/test: `2b11cda` (`feat(single): implement bounded ReAct single shape and extra tests`), `src/lab8/shapes/single.py`, `src/tests/test_single_extra.py` trên nhánh `feature/2A202603602-PhamThiHongNgoc`.
- Kết quả tự kiểm trong `src/`:
  - `.venv/bin/python -m lab8.smoke`: `lab8.smoke pass`.
  - `.venv/bin/python -m pytest -q`: `60 passed, 248 deselected` (54 test host + 6 test trong `tests/test_single_extra.py`).
  - `.venv/bin/python -m pytest -q tests/test_single_extra.py`: `6 passed`.
  - `.venv/bin/python -m pytest -q -m student -o addopts= -k "single]"`: `62 passed, 246 deselected` (đạt 100% 62 test student của Shape B; lưu ý dùng `-k "single]"` vì tên hàm `test_public_single_run_cases` có chữ `single` sẽ match cả các shape khác nếu chỉ dùng `-k single`).
- Mẫu trace kiểm tra: `src/traces/R-single-C-001-s11.json` (6 event, `run_id` khớp `RunResult.run_id`, không chứa secret/PII/ticket).

## 5. Công cụ AI đã dùng

- Sử dụng trợ lý lập trình AI (Antigravity) để rà soát hướng dẫn nhóm (`HUONG_DAN_NHOM.md`), đối chiếu contract của `run_react` trong `src/lab8/runtime.py`, triển khai `single.py` và viết bộ test `test_single_extra.py`.
- Cách tự kiểm tra kết quả: tự chạy các lệnh `lab8.smoke`, `pytest -q`, `pytest -q tests/test_single_extra.py`, `pytest -q -m student -o addopts= -k "single]"` và đọc trực tiếp file trace `src/traces/R-single-C-001-s11.json` để xác minh tính đúng đắn về logic tiền, crash safety và bảo mật trace.

## 6. Tự đánh giá

- Hoàn thành trọn vẹn phần việc của Phạm Thị Hồng Ngọc (Shape B `single` + `test_single_extra.py` + báo cáo), không chạm vào các file thuộc phạm vi của thành viên khác hay các file thước đo bị cấm sửa.
