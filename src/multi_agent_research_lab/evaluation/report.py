"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics

REPORT_HEADER = (
    "| Lần chạy | Độ trễ (s) | Chi phí (USD) | Chất lượng | "
    "Citation coverage | Failure rate | Ghi chú |"
)


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Báo cáo benchmark",
        "",
        "Báo cáo này so sánh các lần chạy theo độ trễ, chi phí ước tính, "
        "quality proxy, citation coverage và failure rate.",
        "",
        REPORT_HEADER,
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        coverage = "" if item.citation_coverage is None else f"{item.citation_coverage:.0%}"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | "
            f"{coverage} | {item.failure_rate:.0%} | {item.notes} |"
        )
    lines.extend(
        [
            "",
            "## Giải thích trace",
            "",
            "- Supervisor route lần lượt qua Researcher, Analyst, Writer rồi `done`.",
            "- Researcher ghi lại nguồn và research notes.",
            "- Analyst chuyển notes thành claim, evidence và rủi ro.",
            "- Writer tạo câu trả lời cuối cùng có citation và metadata token/cost.",
            "",
            "## Failure mode",
            "",
            "Nếu không cấu hình API key live, hệ thống fallback sang local search "
            "và offline LLM synthesis. Cách này giúp test ổn định, nhưng khi cần "
            "nghiên cứu mới theo thời gian thực nên thay bằng provider live.",
        ]
    )
    return "\n".join(lines) + "\n"
