# Báo cáo benchmark

Báo cáo này so sánh baseline một tác tử và workflow đa tác tử theo độ trễ, chi phí ước tính, chất lượng, độ phủ citation và tỉ lệ lỗi. Lần chạy mới nhất đã dùng OpenAI API thật và trả về HTTP 200 OK.

| Lần chạy | Độ trễ (s) | Chi phí (USD) | Chất lượng | Độ phủ citation | Tỉ lệ lỗi | Ghi chú |
|---|---:|---:|---:|---:|---:|---|
| Baseline một tác tử | 14.05 | 0.0000 | 4.0 | 0% | 0% | Không có source riêng; trace có 1 event |
| Workflow đa tác tử | 11.31 | 0.0004 | 10.0 | 100% | 0% | Có 5 source, 9 trace event và citation đầy đủ |

## Giải thích trace

- Supervisor route lần lượt qua `researcher -> analyst -> writer -> done`.
- Researcher thu 5 nguồn từ local corpus và ghi `research_notes`.
- Analyst chuyển research notes thành claim, evidence, weak evidence và gợi ý cấu trúc câu trả lời.
- Writer gọi OpenAI để tạo `final_answer`, gắn citation `[1] [2] [3] [4] [5]` và ghi metadata token/cost.
- Workflow kết thúc sau 4 iteration, không có lỗi trong `state.errors`.

## Kết quả chính

- Baseline chạy thành công với OpenAI nhưng không có độ phủ citation vì không đi qua bước Researcher.
- Workflow đa tác tử có trace rõ hơn, độ phủ citation 100% và quality proxy cao hơn.
- Chi phí của Writer trong lần chạy multi-agent là khoảng `0.00044145 USD`.
- Các bước kiểm tra chất lượng đều pass: `ruff`, `mypy`, `pytest`.

## Chế độ lỗi và cách khắc phục

Chế độ lỗi chính là thiếu API key hoặc provider LLM lỗi. Khi đó hệ thống fallback sang tổng hợp offline và local mock search để vẫn chạy được test. Trong môi trường production, nên cấu hình provider live cho search, bật tracing provider như LangSmith hoặc Langfuse, và lưu trace artifact cho từng lần chạy.

## Log chạy lại

Log từng process nằm trong `reports/run_logs/`:

- `00_key_check.log`: xác nhận key được phát hiện mà không in secret.
- `01_settings_probe.log`: xác nhận app load được OpenAI key và model.
- `02_ruff_check.log`: lint pass.
- `03_mypy.log`: typecheck pass.
- `04_pytest.log`: unit test pass.
- `05_baseline.log`: baseline gọi OpenAI thành công.
- `06_multi_agent.log`: workflow multi-agent gọi OpenAI thành công.
- `07_benchmark.log`: benchmark ghi lại báo cáo này.

## Trace tóm tắt

```text
workflow.build
supervisor.route -> researcher
agent.researcher -> source_count=5
supervisor.route -> analyst
agent.analyst -> analysis_chars=661
supervisor.route -> writer
agent.writer -> output_tokens=624, cost_usd=0.00044145
supervisor.route -> done
workflow.run -> iterations=4, errors=0
```
