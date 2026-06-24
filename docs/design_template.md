# Ghi chú thiết kế

## Bài toán

Hệ thống cần nhận một câu hỏi nghiên cứu dài, thu thập nguồn, phân tích bằng chứng và viết câu trả lời cuối cùng có citation. Ngoài phần trả lời, hệ thống còn phải so sánh được đường cơ sở một tác tử với workflow đa tác tử.

## Vì sao dùng multi-agent?

Một tác tử thường nhanh hơn nhưng dễ trộn lẫn các bước tìm kiếm, phân tích và viết, làm trace khó đọc và khó khoanh vùng lỗi. Bài toán này có ba giai đoạn tự nhiên: Researcher thu thập nguồn, Analyst đánh giá bằng chứng, Writer tổng hợp câu trả lời. Supervisor giữ quyền điều phối để tránh vòng lặp vô hạn và giúp luồng chạy dễ debug.

## Vai trò các agent

| Agent | Trách nhiệm | Input | Output | Chế độ lỗi |
|---|---|---|---|---|
| Supervisor | Chọn bước tiếp theo và dừng an toàn | Toàn bộ `ResearchState` | `route_history`, trace event | Route sai hoặc chạm giới hạn vòng lặp |
| Researcher | Thu thập nguồn và ghi research notes | Query, số nguồn tối đa | `sources`, `research_notes` | Không tìm thấy nguồn hoặc nguồn mock chưa đủ mới |
| Analyst | Rút ra claim, bằng chứng và rủi ro | Sources, research notes | `analysis_notes` | Không phát hiện bằng chứng yếu |
| Writer | Viết câu trả lời cuối cùng | Research notes, analysis notes | `final_answer`, metadata token/cost | Thiếu citation hoặc provider LLM lỗi |

## Trạng thái chung

- `request`: query gốc, audience và giới hạn số nguồn.
- `iteration`: bộ đếm guardrail.
- `route_history`: lịch sử quyết định route của Supervisor.
- `sources`: tài liệu nguồn để tính độ phủ citation.
- `research_notes`: handoff từ Researcher sang Analyst.
- `analysis_notes`: handoff từ Analyst sang Writer.
- `final_answer`: câu trả lời cuối cùng cho người dùng.
- `agent_results`: artifact và metadata cost theo từng agent.
- `trace`: trace JSON phục vụ review.
- `errors`: lỗi và lý do fallback.

## Chính sách điều phối

```text
supervisor
  -> researcher -> supervisor
  -> analyst    -> supervisor
  -> writer     -> supervisor
  -> done
```

Supervisor chọn artifact còn thiếu đầu tiên theo thứ tự `research_notes`, `analysis_notes`, `final_answer`. Nếu đã có `final_answer` hoặc hết budget vòng lặp, Supervisor route sang `done`.

## Guardrail

- Max iterations: `Settings.max_iterations`, mặc định là 6.
- Timeout: `Settings.timeout_seconds`, dùng trong OpenAI client.
- Retry: OpenAI call retry tối đa 2 lần với exponential backoff.
- Fallback: tổng hợp LLM offline, local mock search và câu trả lời dự phòng ở workflow.
- Validation: Pydantic schema kiểm tra độ dài query, số nguồn và khoảng giá trị metric.

## Kế hoạch benchmark

- Query:
  - "Research GraphRAG state-of-the-art and write a 500-word summary"
  - "Compare single-agent and multi-agent workflows for customer support"
  - "Summarize production guardrails for LLM agents"
- Metric:
  - Độ trễ theo giây.
  - Chi phí ước tính bằng USD.
  - Quality proxy dựa trên artifact hoàn thành và việc không có lỗi.
  - Độ phủ citation.
  - Tỉ lệ lỗi.
- Kỳ vọng:
  - Baseline thường đơn giản hơn nhưng traceability và độ phủ citation thấp hơn.
  - Multi-agent chậm hơn một chút nhưng dễ debug, dễ review và giải thích rõ hơn.
