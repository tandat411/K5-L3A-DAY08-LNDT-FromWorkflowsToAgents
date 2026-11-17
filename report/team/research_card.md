# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy: trial fail của swarm ở seed 55 thuộc nhóm lỗi nào của MAST, và bỏ đúng nhóm lỗi đó thì metric đổi ra sao |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025, https://arxiv.org/abs/2503.13657. Loại bằng chứng: taxonomy thực nghiệm, xây bằng gán nhãn tay trên trace của các hệ multi-agent |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent gom được vào 14 failure mode thuộc 3 nhóm: thiết kế hệ thống, lệch pha giữa các agent, và kiểm chứng tác vụ. Taxonomy được gán nhãn tay với độ đồng thuận κ = 0,88 |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Trace lấy từ các framework multi-agent mã nguồn mở chạy LLM thật trên task như lập trình, toán, hỏi đáp. Paper mô tả lỗi xảy ra ở đâu, không đo tần suất trên MockLLM cố định theo seed, và không xét trường hợp có host bằng code chặn ghi như LogiX |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Lỗi R-swarm-C-002-s55 thuộc nhóm kiểm chứng tác vụ: swarm nhận số ngày trễ khách viết trong ticket mà không đối chiếu với dòng order. Nếu thay swarm bằng orchestrator (quote thẳng từ order, không có bước tin ticket) thì pass rate tăng từ 0,986 lên 1,0, pass^5 từ 0,929 lên 1,0, seed variance từ 0,000816 về 0, và cost/success giảm vì bớt 2 lần gọi model (peer, parse) mỗi trial |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool đọc và host, seed 11,22,33,44,55, 14 claim public, `config/pricing.yaml`, `lab8.metrics`, `as_of` 2026-11-15, mỗi trial một SQLite mới. Biến thay đổi: có hay không bước để model đè dữ kiện order bằng chữ trong ticket (swarm có, orchestrator không). Nhiễu đã biết: swarm còn thêm 2 lần gọi model nên chênh cost không quy hết cho bước kiểm chứng; chênh pass rate thì có |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: refund cho claim lẽ ra bị từ chối vì tin số trong ticket (C-002: ticket ghi trễ 5 ngày, order ghi 2 ngày). Đo bằng pass rate, pass^5, seed min-max, seed variance và cost/success theo shape trong `reports/benchmark.json`; đọc trace để thấy event `model_override` |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` (so `by_shape.swarm` với `by_shape.orchestrator` trong cùng file).
- Run id / file report: `R-swarm-C-002-s55` (trial fail duy nhất của swarm), `R-orchestrator-C-002-s55` (trial đối chứng); `src/reports/benchmark.json`.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: ĐÚNG trên bộ public. Từ `src/reports/benchmark.json` (14 claim × 5 seed = 70 trial mỗi shape):

  | Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Model call / trial |
  | --- | --- | --- | --- | --- | --- | --- |
  | swarm (có bước tin ticket) | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 3.00 |
  | orchestrator (không có) | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 47.91 | 1.86 |

  Pass rate, pass^5 và variance đổi đúng hướng và đúng độ lớn dự đoán; trial fail duy nhất là `R-swarm-C-002-s55` (`status resolved != denied`), còn `R-orchestrator-C-002-s55` pass. Trace của trial swarm cho thấy investigator đọc đúng `delay_days: 2`, sau đó event `model_override` đổi thành 5 và quote ra 20.000. Cost/success giảm 3,3%, nhỏ hơn mức "bớt 2 lần gọi model" gợi ý, vì orchestrator thêm lần gọi `plan` và gọi tool `lookup_refund_history`; phần chênh cost vì vậy không quy được cho bước kiểm chứng.
- Bổ sung trên `student_drop/` (40 claim × 5 seed, nhãn viết tay, `src/scripts/doi_chieu_hidden.py` → `src/reports/hidden_doi_chieu.json`, không phải điểm chính thức): swarm 0.970 / pass^5 0.850, orchestrator 1.000 / 1.000. Cả 6 trial fail của swarm đều ở seed 55 và cùng một kiểu lỗi (tin số ngày trong ticket): 5 ca hoàn sai, 1 ca từ chối sai (C-H40, ticket nói ít hơn thực tế). Kết quả này ủng hộ hypothesis trên bộ lớn hơn, nhưng vẫn chỉ có một nhóm lỗi MAST xuất hiện vì lỗi của swarm là lỗi cài cố ý.
- Phân loại: lỗi nằm ở bước kiểm chứng (dữ kiện dùng để quote không được kiểm lại với nguồn có cấu trúc). Cũng có thể đọc là lệch pha giữa các agent, vì bước sau bỏ qua kết quả investigator đã trả. Nhóm chọn nhóm kiểm chứng vì cách sửa đúng là thêm bước đối chiếu trước khi ghi, không phải đổi cách các agent trao đổi.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi của swarm là lỗi cài cố ý theo seed (`seed % 5 == 0`), không phải lỗi tự phát của model; chỉ 1 trial fail nên không đủ để nói về tần suất các nhóm lỗi MAST.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
