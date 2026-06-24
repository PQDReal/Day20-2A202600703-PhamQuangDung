"""Command-line entrypoint for the lab starter."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.storage import LocalArtifactStore

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    response = LLMClient().complete(
        "You are a single-agent research assistant. Answer directly and mention uncertainty.",
        f"Question: {query}\nAudience: {request.audience}",
    )
    state.final_answer = response.content
    state.add_trace_event(
        "baseline.complete",
        {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
        },
    )
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    result = workflow.run(state)
    console.print(result.model_dump_json(indent=2))


@app.command("benchmark")
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Report path under reports/")
    ] = Path("benchmark_report.md"),
) -> None:
    """Run baseline and multi-agent benchmark, then write a markdown report."""

    _init()

    def baseline_runner(item: str) -> ResearchState:
        request = ResearchQuery(query=item)
        state = ResearchState(request=request)
        response = LLMClient().complete(
            "You are a single-agent research assistant. Answer directly.",
            f"Question: {item}\nAudience: {request.audience}",
        )
        state.final_answer = response.content
        state.add_trace_event("baseline.complete", {"cost_usd": response.cost_usd})
        return state

    def multi_runner(item: str) -> ResearchState:
        return MultiAgentWorkflow().run(ResearchState(request=ResearchQuery(query=item)))

    _, baseline_metrics = run_benchmark("single-agent baseline", query, baseline_runner)
    multi_state, multi_metrics = run_benchmark("multi-agent workflow", query, multi_runner)
    report = render_markdown_report([baseline_metrics, multi_metrics])
    report += "\n## Latest Multi-Agent Trace\n\n```json\n"
    report += multi_state.model_dump_json(indent=2)
    report += "\n```\n"
    path = LocalArtifactStore().write_text(output.as_posix(), report)
    console.print(Panel.fit(str(path), title="Benchmark Report Written"))


if __name__ == "__main__":
    app()
