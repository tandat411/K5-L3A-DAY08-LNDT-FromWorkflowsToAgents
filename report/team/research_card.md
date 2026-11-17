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
| CÂU | R1 / R2 / R3 / R4 | R1 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research 2026, *Towards a Science of Scaling Agent Systems*, benchmark trên nhiều task agent; loại bằng chứng: benchmark |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Thêm agent song song chỉ cải thiện hiệu suất trên các task có subtask độc lập; với task tuần tự, scaling số agent làm tăng cost mà không tăng pass rate |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận này được đo trên các LLM thực tế với task có cấu trúc rõ ràng; không áp dụng trực tiếp cho MockLLM hoặc môi trường mô phỏng |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu đổi workflow (không có investigator) sang orchestrator (thêm 1 investigator), pass rate sẽ giữ nguyên (~1.000) vì task xử lý claim là tuần tự (lookup_order → compute_compensation → issue_refund), nhưng cost/success sẽ tăng ~40–70% do overhead handoff và tool call bổ sung |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, tools (lookup_order, compute_compensation, issue_refund), seeds (11,22,33,44,55), corpus (14 public claims), pricing (config/pricing.yaml), evaluator. Biến thay đổi duy nhất: topology — workflow (không có investigator) vs orchestrator (có investigator) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: orchestrator có thể fail thêm nếu handoff bị từ chối do allowlist sai. Đo bằng pass rate và cost/success từ `benchmark.json`. Lỗi phụ: secret leak qua handoff nếu facts chứa field ngoài allowlist — đo bằng secret_leakage trong grader |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn):
  `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: R-workflow-C-001-s11 / src/reports/benchmark.json
- Kết quả so với hypothesis (**đúng**), kèm số liệu:
  - workflow: pass_rate=1.000, pass^5=1.000, variance=0.000, cost/success=27.86 VND
  - orchestrator: pass_rate=1.000, pass^5=1.000, variance=0.000, cost/success=46.43 VND
  - Chênh lệch cost: +66.6% (27.86 → 46.43). Pass rate không đổi. Xác nhận hypothesis: task xử lý claim là tuần tự, thêm investigator không tăng pass rate mà chỉ tăng cost đáng kể.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Với LLM thực tế, investigator có thể giúp xử lý edge case mà MockLLM không mô phỏng được. Kết luận chỉ có giá trị trong setup lab này.
