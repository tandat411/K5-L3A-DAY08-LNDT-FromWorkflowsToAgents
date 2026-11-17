# Báo cáo cá nhân — 2A202603603_Nguyễn Trần Tú Trân

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

**Đối chiếu với phần việc được giao (ledger, crash, evaluation)**

| Việc | Kết quả | Bằng chứng |
| --- | --- | --- |
| Crash suite | Đạt: 20/20 | `src/reports/crash.json` |
| Crash trên shape của nhóm | Đạt: 3 điểm crash, gọi lại, gọi lại sau crash, xanh trên cả 4 shape | `tests/test_crash_shapes.py` |
| Benchmark 4 shape × 5 seed | Đạt: đủ 4 shape, 14 claim, seed 11–55, do công cụ sinh | `src/reports/benchmark.json` |
| Research card + ablation | Đạt phần chạy được; phần ablation còn nhiễu (xem dưới) | `report/team/research_card.md` |
| Must-pass trên bộ public | Không trial nào lộ secret hay refund khi thiếu approval; crash 20/20 | ma trận student 283/283 |
| Tự kiểm trên `student_drop/` | Đạt: 3 shape × 40 claim × 5 seed chạy hết, không lỗi, không `leak_suspect`; chấm bằng nhãn viết tay: 3 shape 1.000 / 1.000, swarm 0.970 / 0.850 | `src/reports/hidden_selfcheck.json`, `src/scripts/doi_chieu_hidden.py`, `src/reports/hidden_doi_chieu.json` |

**Làm được tốt**

- Hiểu rõ ba ranh giới của bài: tiền do `compute_compensation` tính, ticket là dữ liệu chứ không phải lệnh, chỉ host được ghi refund qua `durability.issue_refund` với quote đầy đủ. Đã biến ba ý này thành test (`test_ticket_is_data.py`) thay vì chỉ ghi trong báo cáo.
- Phát hiện crash suite chính thức chỉ kiểm host và swarm, nên viết thêm test crash cho từng shape. Khi một test đỏ, đã đọc `durability.issue_refund` để tìm nguyên nhân (host trả `idempotent_replay` trước mọi điểm crash) rồi sửa test cho đúng hành vi, không sửa cho test xanh.
- Số liệu trong ADR, research card và báo cáo nhóm đều lấy từ file report do công cụ sinh ra, có run id kèm theo.

**Chưa tốt và lý do**

- Phần lớn code ba shape và test được viết cùng trợ lý AI (Claude Code). Tôi kiểm bằng cách chạy test, đọc trace và đối chiếu với luật nghiệp vụ, nhưng mức hiểu từng dòng code của single và orchestrator chưa sâu bằng phần crash và evaluation do tôi phụ trách.
- Code ba shape đều commit dưới tên tôi, nên lịch sử git chưa phản ánh đúng phân công ban đầu (workflow — Đạt, single — Ngọc, orchestrator — Lam). Các bạn bổ sung đóng góp bằng commit test của mình.
- Ablation trong research card (swarm so với orchestrator) thay đổi hơn một biến: ngoài bước tin ticket, hai shape còn khác số lần gọi model. Chênh pass rate quy được cho bước kiểm chứng; chênh cost thì không. Lẽ ra nên dựng một biến thể chỉ khác đúng một yếu tố.
- Bộ `student_drop/` không có nhãn, nên kết luận "không claim nào sai" dựa trên nhãn tôi tự gán theo luật nghiệp vụ; số chính thức chỉ có trên 14 claim public, nơi cả ba shape của nhóm đều đạt 1.000.
- Push lên GitHub bị chặn vì tài khoản bị khoá (HTTP 403), làm chậm việc nộp; nên kiểm quyền push ngay từ CP1.

**Rút ra**

- Với task tuần tự, có luật rõ và dữ liệu có cấu trúc, kiến trúc ít tự chủ nhất (workflow) đạt cùng độ đúng mà rẻ nhất: cost/success 28.48 so với 39.79 (single), 47.91 (orchestrator), 49.57 (swarm).
- Checkpoint một mình không chống ghi trùng được (demo `buggy_workflow` ra 2 dòng refund); phải có ledger với khoá idempotency trong cùng transaction.
- Trace là ranh giới bảo mật: chỉ ghi dữ liệu đã qua allowlist, không ghi nguyên văn ticket.
- Metric phải đọc kèm định nghĩa: cột steps đếm số event trong trace, nên phụ thuộc cách mỗi shape ghi trace chứ không đo khối lượng việc.

**Tự chấm phần việc của mình:** hoàn thành phần ledger, crash, evaluation và tự kiểm trên `student_drop/`; còn thiếu một ablation chỉ đổi đúng một biến.
