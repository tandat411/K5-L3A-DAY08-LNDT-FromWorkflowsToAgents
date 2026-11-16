# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: bc3630f
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên bộ public (14 claim × 5 seed = 70 trial), cả workflow, single và orchestrator đều đạt pass rate = 1.000, pass^5 = 1.000, seed variance = 0. Workflow là shape ít tự chủ nhất trong ba shape đạt ngưỡng, với cost/success thấp nhất (27.86 VND mô phỏng) và số bước ít nhất (mean 1.86, p95 = 2). Theo nguyên tắc "ít tự chủ nhất mà vẫn làm được việc", workflow được chọn vì không cần model loop hay handoff mà vẫn đảm bảo toàn bộ chỉ tiêu.

## Có đáng đổi lấy multi-agent không

Single và orchestrator cho cùng pass rate nhưng tốn thêm 11% và 67% cost so với workflow. Swarm có pass rate thấp hơn (0.986) và variance khác 0 (0.000816) do điểm yếu tham chiếu ở seed 55 — khi ticket ghi số ngày trễ khác DB, swarm tin ticket thay vì DB. Với task xử lý claim tuần tự và dữ liệu tin cậy từ DB, việc thêm agent không mang lại lợi ích đo được. Quyết định sẽ đảo lại nếu: (1) pass rate của workflow trên bộ hidden giảm xuống dưới 0.75, hoặc (2) task yêu cầu tra cứu song song nhiều nguồn mà code cố định không xử lý được.

## Trace và bằng chứng

Workflow ghi các event: `lookup_order` (chỉ ghi visible flag, không ghi order row thô), `quote` (amount_vnd, reason, clause_ids), `decision` (status). Các field cố ý **không** ghi gồm: `phone`, `address`, `internal_note`, `item_name`, `parent_secret`, `raw_headers` — vì đây là thông tin cá nhân và secret không liên quan đến quyết định hoàn tiền; grader scanner sẽ fail nếu chúng xuất hiện trong trace. Secret leakage được kiểm bằng `python -m pytest -q -m student -o addopts=` (248/248 pass) và crash suite (20/20).

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
