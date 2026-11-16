# Báo cáo cá nhân — MSSV_HoTen

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trần Tú Trân
- MSSV: 2A202603603
- Email: 
- GitHub: https://github.com/trannguyentran

## 2. Phần việc phụ trách

Vai ledger, crash và evaluation: crash suite, benchmark, research card, mục Kết quả và Khó khăn của báo cáo nhóm. Ngoài ra tích hợp và chạy kiểm tra cả ba shape `workflow`, `single`, `orchestrator` trên máy mình.

## 3. Đóng góp cụ thể

- `f105423`: hướng dẫn nhóm (`HUONG_DAN_NHOM.md`): phân tích đề, luật nghiệp vụ, phân công, lộ trình CP1–CP5.
- `5d0719b`: `src/tests/test_ticket_is_data.py` — `RunResult` chỉ nhận 5 status; `compute_compensation` trả 0 cho C-002, C-006, C-009 dù ticket viết gì; ticket C-002 ghi trễ 5 ngày trong khi order ghi 2; ba shape phải `denied` C-002 ở cả 5 seed.
- `41728aa`: ba shape, `src/tests/test_crash_shapes.py`, `src/reports/benchmark.json`, `src/reports/crash.json`.
- Quyết định kỹ thuật:
  - Không ghi nguyên văn ticket vào trace ở cả ba shape, vì đó là chữ khách viết, có thể chứa thông tin cá nhân hoặc chuỗi injection; trace chỉ ghi cờ `has_order_id`.
  - Orchestrator dùng `facts={}` trong handoff để investigator tự đọc dữ kiện từ database thay vì nhận lại từ orchestrator.
  - Thêm test crash cho từng shape vì `lab8.crash_test` chỉ kiểm host và swarm, còn T12 chỉ kiểm một điểm crash.
  - Research card chọn R2 (MAST) và dùng chính trial fail của swarm làm dữ liệu.

## 4. Bằng chứng

- Commit `41728aa`, `5d0719b`, `f105423` trên nhánh `feature/2A202603603-NguyenTranTuTran`.
- Test: `tests/test_ticket_is_data.py`, `tests/test_crash_shapes.py` (`test_crash_then_resume_pays_once`, `test_repeated_calls_keep_one_refund`, `test_retry_after_crash_is_replay_not_new_write`).
- `src/reports/crash.json`: `crash_safety` = 20/20.
- `src/reports/benchmark.json`: workflow 1.000 / 1.000 / variance 0 / cost/success 28.48; swarm 0.986 / 0.929 / 0.000816 / 49.57.
- Run id: `R-swarm-C-002-s55` (trial fail duy nhất, trace có event `model_override` đổi `delay_days` 2 → 5), `R-orchestrator-C-002-s55` (đối chứng, pass).

## 5. Công cụ AI đã dùng

- Claude Code (trợ lý lập trình chạy trong VS Code): đọc toàn bộ đề và code host, viết hướng dẫn nhóm, viết ba shape, viết test, chạy benchmark và crash suite, soạn nháp ADR, research card và báo cáo nhóm.
- Cách kiểm tra:
  - Chạy `python -m pytest -q` (165 passed) và `python -m pytest -q -m student -o addopts=` (283 passed).
  - Chạy `python -m lab8.check_submission`.
  - Mở trace của C-005 và C-010 để kiểm không có SĐT, địa chỉ, tên hàng, ghi chú nội bộ; quét mọi trace tìm `CANARY`, `parent_secret`, `raw_headers`, `Bearer`.
  - Mọi số trong báo cáo lấy từ `src/reports/*.json` do công cụ sinh ra, không chép tay.
- Một lỗi do AI gây ra đã phát hiện qua chạy test: bản đầu của `test_crash_shapes.py` giả định gọi lại sau crash sẽ crash lần nữa; swarm báo `DID NOT RAISE`; đọc `durability.issue_refund` thì thấy host trả `idempotent_replay` trước mọi điểm crash, nên sửa test theo hành vi đúng.

## 6. Tự đánh giá

...
