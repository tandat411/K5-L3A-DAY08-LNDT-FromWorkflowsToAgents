# Báo cáo cá nhân — Nguyễn Thùy Lam

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thùy Lam
- MSSV: `2A202603632`
- Email: `26ai.lamnt5@vinuni.edu.vn`
- GitHub: [ThuyLam4719](https://github.com/ThuyLam4719)
- Nhóm: LNDT · Lớp L3A H202

## 2. Phần việc phụ trách

Em phụ trách **Shape C — Orchestrator + handoff** trong [orchestrator.py](../../src/lab8/shapes/orchestrator.py). Công việc gồm điều phối các bước tra cứu claim, giới hạn dữ liệu và quyền của investigator, chuyển đề xuất hoàn tiền sang host, và ghi trace theo contract. Phần test cá nhân được phân công kiểm tra trace của `C-001` đến `C-014` và quyền truy cập công cụ trong handoff.

## 3. Đóng góp cụ thể

- **Giới hạn dữ liệu và quyền qua handoff.** Shape C sử dụng `make_handoff()` để tạo `handoff.v1` với `facts={}` và ba công cụ chỉ đọc là `lookup_order`, `lookup_refund_history` và `compute_compensation`. Investigator tra cứu đơn trong phạm vi quyền của principal. Trace ghi handoff đã lọc, cờ `visible` và kết quả tra cứu lịch sử hoàn tiền. Cách này giữ dữ liệu phục vụ kiểm tra mà tránh ghi nguyên claim, nguyên order, `parent_secret` hoặc `raw_headers`.
- **Tách tính đề xuất khỏi ghi hoàn tiền.** `compute_compensation` tính quote từ dữ liệu đơn hàng có cấu trúc và luật nghiệp vụ. Nếu thiếu mã đơn, Shape C trả `needs_info`. Nếu đơn không tìm thấy hoặc principal không có quyền xem, shape trả `escalated`. Quote bằng `0` dẫn đến `denied` ngay tại shape. Với quote dương, orchestrator chuyển **toàn bộ quote** vào `durability.issue_refund()` để host kiểm approval, áp trần theo đơn và ghi ledger khi đủ điều kiện.
- **Giữ đúng số tiền đề xuất và số tiền thực hoàn.** Ở `C-014`, quote là `150.000 VND` và đơn đã được hoàn `30.000 VND`. Shape giữ `proposal_amount = 150000`, còn host ghi `120.000 VND`. Trừ khoản đã hoàn ngay trong shape sẽ khiến host trừ lần thứ hai. Ở `C-013`, đơn đã được hoàn đủ, nên host từ chối quote dương và ghi audit `policy_denied`.
- **Hỗ trợ chạy lại sau crash.** Shape chuyển `crash_at` vào `issue_refund()` và để `InjectedCrash` truyền ra cho bộ kiểm thử. Khi chạy lại, host dùng khóa `refund:{claim_id}` để giữ một khoản hoàn duy nhất. Các nhánh trả `RunResult`, kể cả nhánh kết thúc sớm, đi qua `finish()` để ghi trace theo cùng contract.

## 4. Bằng chứng

| Hạng mục | Bằng chứng |
| --- | --- |
| Ma trận kiểm thử Shape C | `62 passed` khi chạy lại trên bản mã nguồn dùng cho báo cáo. [Ma trận test public](../../src/tests/test_public_matrix.py) bao gồm `test_t11_retry_keeps_one_refund` và `test_t12_crash_before_checkpoint_does_not_double_pay`. |
| Benchmark public | `70/70` trial đạt trên 14 claim × 5 seed. Pass rate và pass^5 đều `1.000`, seed variance `0`, chi phí mô phỏng `46,43 VND` trên mỗi trial đạt, số bước trung bình `2,79`, p95 `3`, số lần gọi model trung bình `0`. Run ID minh họa `R-orchestrator-C-001-s11`. [Kết quả benchmark](../../src/reports/benchmark.json) |
| Commit kỹ thuật cá nhân | `[Điền hash và link commit do ThuyLam4719 đứng tên sau khi đẩy lên GitHub]` |
| Test cá nhân theo C8 | `[Điền tên hàm test thực tế trong src/tests/test_orchestrator_extra.py và kết quả chạy]`. Phạm vi được phân công là đọc trace của `C-001` đến `C-014`, kiểm tra ba chuỗi `CANARY_SECRET_`, `parent_secret`, `raw_headers` đều vắng mặt, và xác nhận các handoff được tạo chỉ cấp công cụ đọc. |

Lệnh tái lập ma trận Shape C từ thư mục `src/`:

```bash
python -m pytest -q -m student -o addopts= -k orchestrator
```

## 5. Công cụ AI đã dùng

Em dùng ChatGPT để giải thích yêu cầu checkpoint, tham khảo cách triển khai `orchestrator.py` ở CP2 và hỗ trợ soạn báo cáo. 

## 6. Tự đánh giá

Trên bộ public, Shape C và workflow cùng đạt `70/70` trial, trong khi Shape C tốn `46,43 VND` mô phỏng trên mỗi trial đạt, cao hơn mức `27,86 VND` của workflow. Với luồng xử lý claim hiện tại, kết quả này ủng hộ lựa chọn workflow của nhóm. 

Qua việc triển khai Shape C, em hiểu rõ hơn cách giới hạn dữ liệu và quyền của investigator thông qua handoff, đồng thời giao việc kiểm tra approval và ghi hoàn tiền cho host.