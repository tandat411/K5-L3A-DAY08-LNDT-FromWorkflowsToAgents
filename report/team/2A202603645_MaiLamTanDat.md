# Báo cáo cá nhân — 2A202603645_MaiLamTanDat

## 1. Thông tin thành viên

- Họ tên: Mai Lâm Tấn Đạt
- MSSV: 2A202603645
- Email: 26ai.datmlt@vinuni.edu.vn
- GitHub: https://github.com/tandat411

## 2. Phần việc phụ trách

- Trưởng nhóm (Team Leader): Quản trị repository, điều phối phân công công việc và tích hợp các nhánh (integration).
- Phụ trách Shape A: Deterministic Workflow (`src/lab8/shapes/workflow.py`).
- Viết test kiểm thử kiểm chứng tính kiên định của workflow (`src/tests/test_workflow_extra.py`).

## 3. Đóng góp cụ thể

- Hiện thực Shape A (`src/lab8/shapes/workflow.py`) theo thiết kế tối giản (Simplicity First):
  - Đọc claim và order hoàn toàn qua allowlist view (`get_claim_view`, `lookup_order`), loại bỏ triệt để nguy cơ rò rỉ secret (`parent_secret`) và PII (SĐT, địa chỉ, hàng hóa).
  - Quyết định tiền bồi thường bằng code thuần (`compute_compensation`), giữ `model_calls = 0` để tối ưu chi phí và triệt tiêu độ biến thiên (variance = 0).
  - Đáp ứng chuẩn crash safety: chuyển `crash_at` vào `durability.issue_refund`, ghi nhận sự kiện crash vào trace và cho phép `InjectedCrash` lan truyền ra ngoài theo đúng yêu cầu test T12.
- Viết bộ kiểm thử `src/tests/test_workflow_extra.py` kiểm chứng ca `C-002` luôn bị từ chối (`status="denied"`, `proposal_amount=0`) qua cả 5 seeds (11, 22, 33, 44, 55), khắc phục hoàn toàn điểm yếu cố ý của Swarm reference.
- Commit chính: `9c18c0b` (`feat(workflow): implement deterministic workflow shape and verification test`).

## 4. Bằng chứng

- Commit hash: `9c18c0b`
- File test: `src/tests/test_workflow_extra.py` (5/5 passed).
- Kết quả ma trận test student: `python -m pytest -q -m student -o addopts= -k workflow` -> 62/62 passed (100%).
- Kiểm tra bài nộp: `python -m lab8.check_submission` ghi nhận:
  - `[ OK ] shape workflow: format đúng, 12/12 claim public pass ở seed 11`
  - `[ OK ] TEAM.md: bảng đóng góp có 1 thành viên`

## 5. Công cụ AI đã dùng

- Công cụ: Antigravity Agent (Gemini 3.8 Flash High).
- Mục đích: Hỗ trợ rà soát rubric chấm điểm, đối chiếu các nguyên lý Andrej Karpathy nhằm đơn giản hóa code và xây dựng kịch bản kiểm thử góc (corner cases).
- Cách tự kiểm tra kết quả: Tự rà soát từng dòng code để đảm bảo không leak PII/secret; kiểm chứng độc lập bằng hệ thống lệnh test tự động của lab (`pytest -q`, `pytest -q -m student -o addopts= -k workflow`, `smoke.py`, `check_submission.py`).

## 6. Tự đánh giá

- Đạt yêu cầu đầy đủ và chất lượng cao cho phần việc phụ trách Shape A.
- Code ngắn gọn, an toàn, không có abstraction thừa, pass rate 100% trên toàn bộ các ca kiểm thử public.
