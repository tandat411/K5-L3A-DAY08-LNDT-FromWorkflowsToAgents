# Team

## Thông tin nhóm

- Tên nhóm: LNDT
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-LNDT-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/tandat411/K5-L3A-DAY08-LNDT-FromWorkflowsToAgents

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Mai Lâm Tấn Đạt | 2A202603645 | 26ai.datmlt@vinuni.edu.vn | https://github.com/tandat411 | Trưởng nhóm |
|   2 | Phạm Thị Hồng Ngọc | 2A202603602 | 26ai.ngocpth@vinuni.edu.vn | https://github.com/ngoc11224756 | Thành viên — Single agent (B) |
|   3 | Nguyễn Thuỳ Lam | 2A202603632 | 26ai.lamnt5@vinuni.edu.vn | https://github.com/ThuyLam4719 | Thành viên |
|   4 | Nguyễn Trần Tú Trân | 2A202603603 | 26ai.tranntt@vinuni.edu.vn | https://github.com/trannguyentran1997 | Thành viên |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Mai Lâm Tấn Đạt | workflow + integration | `9c18c0b` | test_workflow_extra.py |
| Phạm Thị Hồng Ngọc (2A202603602) | Single agent (B) | `2b11cda`, `ebcf04a` (`feat(single)`, `test(single)`) | `src/tests/test_single_extra.py` |
| Nguyễn Thuỳ Lam (2A202603632) | Orchestrator + handoff (C) | `94cb1d4` | `src/tests/test_orchestrator_extra.py` |
| Nguyễn Trần Tú Trân | Ledger, crash, evaluation; tích hợp ba shape | 41728aa (3 shape, crash test, benchmark, crash suite), 5d0719b (test nền tảng), f105423 (hướng dẫn nhóm) | `src/tests/test_ticket_is_data.py`, `src/tests/test_crash_shapes.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603645_MaiLamTanDat

### Phần việc phụ trách

- Trưởng nhóm (Leader), phụ trách Shape A (`src/lab8/shapes/workflow.py`), điều phối và tích hợp nhóm.

### Đóng góp cụ thể

- Cài đặt Shape A (`workflow.py`) dạng deterministic workflow, chi phí 0 token, đạt 100% pass rate.
- Viết test kiểm chứng `src/tests/test_workflow_extra.py` (C-002 denied ở cả 5 seeds).
- Commit: `9c18c0b`.

### Bằng chứng

- Chi tiết xem tại báo cáo cá nhân: [report/team/2A202603645_MaiLamTanDat.md](report/team/2A202603645_MaiLamTanDat.md)

## 2A202603632_NguyenThuyLam

### Phần việc phụ trách

- Phụ trách Shape C (`src/lab8/shapes/orchestrator.py`): Orchestrator + handoff cho investigator chỉ đọc.

### Đóng góp cụ thể

- Dựng handoff chỉ chứa allowlist field, cấp 3 read-only tools (`lookup_order`, `lookup_refund_history`, `compute_compensation`), loại bỏ `parent_secret` và `raw_headers`.
- Đảm bảo ranh giới tính tiền bằng code, truyền full quote vào `durability.issue_refund`, không nuốt `InjectedCrash`.
- Viết test `src/tests/test_orchestrator_extra.py` (20 passed). Commit: `94cb1d4`.

### Bằng chứng

- Chi tiết xem tại báo cáo cá nhân: [report/team/2A202603632_NguyenThuyLam.md](report/team/2A202603632_NguyenThuyLam.md)

## 2A202603603_NguyenTranTuTran

### Phần việc phụ trách

- Phụ trách Ledger, crash test, evaluation, benchmark 4 shape, research card và tích hợp hệ thống.

### Đóng góp cụ thể

- Viết `test_ticket_is_data.py` (commit `5d0719b`), `test_crash_shapes.py` (commit `41728aa`), chạy bộ crash suite 20/20 (`reports/crash.json`) và benchmark 4 shape (`reports/benchmark.json`).
- Viết phiếu nghiên cứu R2 (MAST) trong `research_card.md` và tự kiểm tra bộ hidden `student_drop/`.

### Bằng chứng

- Chi tiết xem tại báo cáo cá nhân: [report/team/2A202603603_NguyenTranTuTran.md](report/team/2A202603603_NguyenTranTuTran.md)

## 2A202603602_PhamThiHongNgoc

### Phần việc phụ trách

- Viết Shape B (`src/lab8/shapes/single.py`) dùng vòng lặp ReAct tối đa 8 bước và bộ test riêng `src/tests/test_single_extra.py`.

### Đóng góp cụ thể

- Cài đặt `decide` trong `run_react(..., max_steps=8)` chỉ gọi 4 tool đọc (`get_claim_view`, `lookup_order`, `lookup_refund_history`, `compute_compensation`), đếm model call qua `mock_llm.complete`, không tin số ngày/chỉ thị trong `ticket`.
- Xử lý phần quyết định sau vòng lặp bằng code: giữ nguyên quote đầy đủ khi gọi `durability.issue_refund(..., crash_at=crash_at)` (T13/T14), không nuốt `InjectedCrash`, và ghi trace sạch secret/PII/ticket qua `finish()`.
- Viết 6 test trong `src/tests/test_single_extra.py` kiểm tra giới hạn 8 bước, spy `runtime.dispatch` để xác nhận chỉ dùng `READONLY_TOOLS`, chống bẫy ticket ở cả 5 seed, T13/T14, bảo mật trace và crash/resume ở `C-012`.

### Bằng chứng

- Commit `2b11cda` và `ebcf04a` trên nhánh `feature/2A202603602-PhamThiHongNgoc`, `src/lab8/shapes/single.py`, `src/tests/test_single_extra.py`, `report/team/2A202603602_PhamThiHongNgoc.md` (`62 passed` cho `single` ở ma trận student, `60 passed` cho cổng host + `test_single_extra.py`).
