# Hướng dẫn Lab: Hệ thống nghiên cứu đa tác tử

## Bối cảnh

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Đường cơ sở một tác tử**: một agent làm toàn bộ.
2. **Workflow đa tác tử**: Supervisor điều phối Researcher, Analyst và Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có trách nhiệm riêng.
- Trạng thái chung phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ đánh giá output bằng cảm tính.

## Mốc 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

Baseline đã dùng `LLMClient.complete`. Khi có `OPENAI_API_KEY`, client gọi OpenAI; khi không có key, client dùng tổng hợp offline để vẫn chạy được kiểm tra nhanh và benchmark.

## Mốc 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

Supervisor routing policy đã triển khai:

- Gọi Researcher khi chưa có `research_notes`.
- Gọi Analyst khi đã có research nhưng chưa có `analysis_notes`.
- Gọi Writer khi research và analysis đã sẵn sàng.
- Dừng khi có `final_answer` hoặc chạm `max_iterations`.
- Nếu worker fail, workflow ghi vào `state.errors`; Writer có câu trả lời dự phòng.

## Mốc 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

Các worker agent đã triển khai:

- Researcher: tìm trong local corpus, khử trùng lặp source, ghi research notes có số thứ tự.
- Analyst: rút claim, evidence, weak evidence và đề xuất cấu trúc trả lời.
- Writer: tổng hợp final answer có citation reference và metadata token/cost.

## Mốc 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | Wall-clock time |
| Cost | Token usage hoặc provider usage |
| Quality | Rubric 0-10 do peer review |
| Citation coverage | Số claim có source / tổng claim chính |
| Failure rate | Số query lỗi / tổng số query |

## Câu hỏi kết thúc

Mỗi nhóm trả lời 2 câu:

1. Case nào nên dùng multi-agent? Vì sao?
2. Case nào không nên dùng multi-agent? Vì sao?
