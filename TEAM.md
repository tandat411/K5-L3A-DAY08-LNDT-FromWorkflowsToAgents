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
|   2 | Phạm Thị Hồng Ngọc | 2A202603602 | | https://github.com/ngoc11224756 | Thành viên — Single agent (B) |
|   3 | Nguyễn Thuỳ Lam | 2A202603632 | | https://github.com/ThuyLam4719 | Thành viên |
|   4 | Nguyễn Trần Tú Trân | 2A202603603 | | https://github.com/trannguyentran | Thành viên |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Thị Hồng Ngọc (2A202603602) | Single agent (B) | `2b11cda`, `ebcf04a` (`feat(single)`, `test(single)`) | `src/tests/test_single_extra.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202603602_PhamThiHongNgoc

### Phần việc phụ trách

- Viết Shape B (`src/lab8/shapes/single.py`) dùng vòng lặp ReAct tối đa 8 bước và bộ test riêng `src/tests/test_single_extra.py`.

### Đóng góp cụ thể

- Cài đặt `decide` trong `run_react(..., max_steps=8)` chỉ gọi 4 tool đọc (`get_claim_view`, `lookup_order`, `lookup_refund_history`, `compute_compensation`), đếm model call qua `mock_llm.complete`, không tin số ngày/chỉ thị trong `ticket`.
- Xử lý phần quyết định sau vòng lặp bằng code: giữ nguyên quote đầy đủ khi gọi `durability.issue_refund(..., crash_at=crash_at)` (T13/T14), không nuốt `InjectedCrash`, và ghi trace sạch secret/PII/ticket qua `finish()`.
- Viết 6 test trong `src/tests/test_single_extra.py` kiểm tra giới hạn 8 bước, spy `runtime.dispatch` để xác nhận chỉ dùng `READONLY_TOOLS`, chống bẫy ticket ở cả 5 seed, T13/T14, bảo mật trace và crash/resume ở `C-012`.

### Bằng chứng

- Commit `2b11cda` và `ebcf04a` trên nhánh `feature/2A202603602-PhamThiHongNgoc`, `src/lab8/shapes/single.py`, `src/tests/test_single_extra.py`, `report/team/2A202603602_PhamThiHongNgoc.md` (`62 passed` cho `single` ở ma trận student, `60 passed` cho cổng host + `test_single_extra.py`).
