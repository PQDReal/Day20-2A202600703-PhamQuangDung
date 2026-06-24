# Lab 20: Hệ thống nghiên cứu đa tác tử

Repo bài lab **Multi-Agent Systems**: xây dựng hệ thống trợ lý nghiên cứu gồm **Supervisor + Researcher + Analyst + Writer** và benchmark với đường cơ sở một tác tử.

Repo đã triển khai luồng chạy đầy đủ, có cơ chế dự phòng offline để kiểm tra nhanh không cần API key, và vẫn hỗ trợ OpenAI khi cấu hình `OPENAI_API_KEY`.

## Mục tiêu học tập

Sau bài lab, học viên cần có thể:

1. Thiết kế vai trò rõ ràng cho nhiều tác tử.
2. Xây dựng trạng thái chung đủ thông tin cho quá trình bàn giao.
3. Thêm guardrail tối thiểu: giới hạn vòng lặp, timeout, retry/dự phòng và validation.
4. Ghi trace được luồng chạy và giải thích tác tử nào làm gì.
5. Benchmark một tác tử và đa tác tử theo chất lượng, độ trễ và chi phí.

## Kiến trúc mục tiêu

```text
User Query
   |
   v
Supervisor / Router
   |------> Researcher Agent  -> research_notes
   |------> Analyst Agent     -> analysis_notes
   |------> Writer Agent      -> final_answer
   |
   v
Trace + Báo cáo benchmark
```

## Cấu trúc repo

```text
.
├── src/multi_agent_research_lab/
│   ├── agents/              # Giao diện và implementation của các agent
│   ├── core/                # Config, state, schema, lỗi miền ứng dụng
│   ├── graph/               # Workflow do Supervisor điều phối
│   ├── services/            # LLM, search, storage client
│   ├── evaluation/          # Benchmark và render báo cáo
│   ├── observability/       # Logging và tracing hook
│   └── cli.py               # CLI entrypoint
├── configs/                 # Cấu hình YAML cho bài lab
├── docs/                    # Hướng dẫn lab, rubric, ghi chú thiết kế
├── tests/                   # Unit test
├── notebooks/               # Notebook entrypoint tùy chọn
├── scripts/                 # Script hỗ trợ
├── .env.example             # Mẫu biến môi trường, không chứa secret thật
├── pyproject.toml           # Cấu hình Python project
├── Dockerfile               # Runtime/dev bằng container
└── Makefile                 # Các lệnh thường dùng
```

## Khởi động nhanh

### 1. Tạo môi trường

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e "[dev]"
cp .env.example .env
```

### 2. Cấu hình API key

Mở `.env` và điền key cần thiết. Không commit `.env` lên GitHub.

```bash
OPENAI_API_KEY=...
# tùy chọn
LANGSMITH_API_KEY=...
TAVILY_API_KEY=...
```

### 3. Chạy kiểm tra nhanh

```bash
make test
python -m multi_agent_research_lab.cli --help
```

### 4. Chạy baseline một tác tử

```bash
python -m multi_agent_research_lab.cli baseline \
  --query "Research GraphRAG state-of-the-art and write a 500-word summary"
```

Lệnh này chạy đường cơ sở một tác tử thông qua `LLMClient`. Nếu chưa có API key, client dùng dự phòng offline và vẫn ghi metadata token/cost.

### 5. Chạy workflow đa tác tử

```bash
python -m multi_agent_research_lab.cli multi-agent \
  --query "Research GraphRAG state-of-the-art and write a 500-word summary"
```

Lệnh này chạy luồng `Supervisor -> Researcher -> Analyst -> Writer -> done` và in toàn bộ trạng thái chung kèm trace.

### 6. Tạo báo cáo benchmark

```bash
python -m multi_agent_research_lab.cli benchmark \
  --query "Research GraphRAG state-of-the-art and write a 500-word summary"
```

Kết quả được ghi vào `reports/benchmark_report.md`, gồm độ trễ, chi phí ước tính, quality proxy, độ phủ citation, tỉ lệ lỗi và phần giải thích trace.

## Các mốc triển khai

| Thời lượng | Mốc | File gợi ý |
|---:|---|---|
| 0-15' | Setup, chạy baseline | `cli.py`, `services/llm_client.py` |
| 15-45' | Xây Supervisor/router | `agents/supervisor.py`, `graph/workflow.py` |
| 45-75' | Thêm Researcher, Analyst, Writer | `agents/*.py`, `core/state.py` |
| 75-95' | Trace + benchmark single vs multi | `observability/tracing.py`, `evaluation/benchmark.py` |
| 95-115' | Peer review theo rubric | `docs/peer_review_rubric.md` |
| 115-120' | Câu hỏi kết thúc | `docs/lab_guide.md` |

## Quy ước production trong repo

- Tách rõ `agents`, `services`, `core`, `graph`, `evaluation`, `observability`.
- Không hard-code API key trong code.
- Input/output chính dùng Pydantic schema.
- Có type hints, linting, formatting và unit test tối thiểu.
- Có logging/tracing hook ngay từ đầu.
- Không để agent chạy vô hạn: dùng `max_iterations`, `timeout_seconds`.
- Có benchmark report thay vì chỉ demo output đẹp.

## Phần đã hoàn thành

1. `LLMClient` hỗ trợ OpenAI và dự phòng offline.
2. `SearchClient` có local mock corpus để chạy ổn định.
3. Supervisor routing policy chọn lần lượt `researcher`, `analyst`, `writer`, `done`.
4. Researcher, Analyst, Writer và Critic tùy chọn đã cập nhật shared state.
5. Workflow có điều kiện dừng, giới hạn vòng lặp và câu trả lời dự phòng.
6. Trace JSON ghi từng bước trong `state.trace`.
7. Báo cáo benchmark có metric cụ thể và giải thích trace.

## Sản phẩm nộp

Học viên nộp:

1. GitHub repo cá nhân.
2. Screenshot trace hoặc link trace.
3. `reports/benchmark_report.md` so sánh một tác tử và đa tác tử.
4. Một đoạn giải thích chế độ lỗi và cách khắc phục.

## Tài liệu tham khảo

- Anthropic: Building effective agents — https://www.anthropic.com/engineering/building-effective-agents
- OpenAI Agents SDK orchestration/handoffs — https://developers.openai.com/api/docs/guides/agents/orchestration
- LangGraph concepts — https://langchain-ai.github.io/langgraph/concepts/
- LangSmith tracing — https://docs.smith.langchain.com/
- Langfuse tracing — https://langfuse.com/docs
