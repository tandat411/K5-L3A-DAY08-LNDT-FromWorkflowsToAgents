# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 41728aa
- Run id dẫn chứng: R-workflow-C-002-s55 (pass) đối chứng R-swarm-C-002-s55 (fail); R-workflow-C-014-s11 (trần theo đơn); src/reports/benchmark.json
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (14 claim public × seed 11,22,33,44,55 = 70 trial)
- Cost per success (mô phỏng, VND): 28.48 (tổng 1993.70 / 70 trial pass)
- Crash safety: 20/20 (src/reports/crash.json); T11, T12 và tests/test_crash_shapes.py xanh cho workflow
- Secret leak / approval bypass: 0 / 0 trên bộ public (không trial nào fail vì forbidden_substring; T07, T13 bị host chặn, có policy_denied)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng 14 claim public, cùng 5 seed, cùng MockLLM, bảng giá và evaluator (`src/reports/benchmark.json`), cả ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000, variance 0; swarm đạt 0.986 / 0.929 / 0.000816 vì fail đúng một trial `R-swarm-C-002-s55` (tin "trễ 5 ngày" trong ticket thay vì `delay_days` = 2). Khi độ đúng ngang nhau, workflow rẻ nhất: cost/success 28.48 VND so với 39.79 (single), 47.91 (orchestrator), 49.57 (swarm); trung bình 0.64 lần gọi model và 2.79 lần gọi tool mỗi trial, so với 5.29 / 3.64 của single và 1.86 / 4.64 của orchestrator. Workflow cũng ít tự chủ nhất: mọi nhánh quyết định là code đọc được, không có bước nào để model chọn tool hay sửa dữ kiện, nên dễ kiểm và dễ giải thích khi người chấm hỏi. Đây là kiến trúc ít tự chủ nhất mà vẫn làm được việc.

## Có đáng đổi lấy multi-agent không

Không, với task này. Single và orchestrator không tăng pass rate (đã 1.000 như workflow) mà tốn thêm 40% và 68% cost/success. Swarm vừa đắt hơn 74% vừa kém ổn định hơn. Task claims là chuỗi tuần tự: quote phụ thuộc order, ghi phụ thuộc quote, nên không có phần việc độc lập để agent song song tận dụng.

Quyết định sẽ đảo lại khi:

- Ticket thật sự mơ hồ và cần hỏi lại khách hoặc trích xuất thông tin không có trong database (ví dụ mô tả hư hỏng bằng chữ) — lúc đó một agent đọc hiểu có giá trị mà code cố định không có.
- Phải tra nhiều nguồn độc lập tốn thời gian (nhiều hãng vận chuyển, nhiều hệ thống) mà latency thật đáng kể — investigator song song mới có lợi. MockLLM không đo latency nên lab này không trả lời được câu đó.
- Trên bộ hidden, workflow fail ở loại claim mà single/orchestrator pass. Nhóm chưa có số hidden (chưa có `student_drop/`), nên kết luận hiện chỉ dựa trên bộ public.

Ghi chú về cột steps: metric này đếm số event trong trace, không đếm số bước xử lý. Single ghi hai event mỗi lượt ReAct (observe, act) nên ra 10.79; swarm ghi ít event nên ra 2.80. Không nên đọc cột này như "swarm làm ít việc nhất".

## Trace và bằng chứng

Trace workflow ghi các event: `claim` (chỉ `claim_id` và cờ `has_order_id`), `lookup_order` (kết quả `lookup_order` đã allowlist 7 field: order_id, status, delay_days, shipping_fee_vnd, paid_vnd, damage_verified, carrier; nhánh không visible chỉ ghi reason), `quote` (amount_vnd, reason, clause_ids, parts), `issue_refund` (ok, reason), `decision` (status, proposal_amount, reason), và `crash` khi bị tiêm crash. Mọi nhánh return đều đi qua `finish()` nên luôn có trace của chính lần chạy.

Cố ý không ghi: nguyên văn ticket (chữ khách viết có thể chứa thông tin cá nhân hoặc chuỗi injection), `parent_secret` và `raw_headers` (không bao giờ đọc vì dùng `get_claim_view` thay cho `SELECT *`), SĐT, địa chỉ, tên hàng, ghi chú nội bộ của order (không đọc vì dùng `lookup_order`). Orchestrator ghi handoff sau `make_handoff`/`sanitize`, không ghi parent context. Shape không in gì ra stdout và không ghi file nào ngoài `traces/<run_id>.json`.

Nếu trace nằm ngoài chỗ scanner quét được thì không chứng minh được hệ thống sạch; vì vậy nhóm giữ trace trong `traces/<run_id>.json` đúng contract v1 và không ghi log nào khác. Bằng chứng: 283/283 test ma trận student xanh, trong đó có kiểm `forbid_substrings` cho C-005 và C-010 (SĐT, địa chỉ, tên hàng, ghi chú nội bộ), và một lần quét thủ công mọi file trong `traces/` không thấy `CANARY`, `parent_secret`, `raw_headers`, `Bearer` hay dữ liệu cá nhân của order.

## Giới hạn

MockLLM không phải model sản xuất: nó cố định theo seed, không đọc hiểu ticket, nên ưu thế đọc hiểu của agent thật không thể hiện được ở đây. Cost là giá mô phỏng từ `config/pricing.yaml`, không phải hóa đơn API. Latency để `unavailable`. Số liệu chỉ trên 14 claim public; điểm hidden do giảng viên chấm. Không sửa JSON cho đủ 0.75.
