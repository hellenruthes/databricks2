from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import mlflow
from crewai import Agent, Crew, LLM, Task


from common.secrets import get_secret  


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate weekly report with CrewAI and log to MLflow.")

    # Inputs de negócio
    p.add_argument("--week_of", required=True, help="Week reference date (e.g., 2026-01-05).")
    p.add_argument("--topics", required=True, help="Topics to cover in the weekly report.")
    p.add_argument("--data", default="", help="Optional data/context for the report (string/JSON).")

    # Modelo
    p.add_argument("--model", default="gpt-4o-mini", help="LLM model name.")

    # Secrets
    p.add_argument("--secret_scope", default="hellendev2", help="Databricks secret scope.")
    p.add_argument("--openai_key_name", default="openaiapi", help="Secret key name for OpenAI API key.")

    # MLflow
    p.add_argument("--experiment", default="/weekly-report", help="MLflow experiment path.")
    p.add_argument("--run_name", default=None, help="Optional MLflow run name (overrides default).")
    p.add_argument("--prompt_version", default="v1", help="Tag to version prompts.")

    # Output/Artifacts
    p.add_argument(
        "--artifact_dir",
        default="artifacts",
        help="Local dir to write artifacts before logging to MLflow.",
    )

    # Logging
    p.add_argument("--verbose", action="store_true", help="Enable verbose agent logs.")

    return p


def main() -> None:
    args = build_parser().parse_args()

    # ----- Secrets & env -----
    os.environ["CREWAI_TESTING"] = "true"
    os.environ["OPENAI_API_KEY"] = get_secret(key=args.openai_key_name, scope=args.secret_scope)

    # ----- Prompt inputs -----
    report_structure = f"""
Data Weekly Update [Week of Date]:spiral_calendar_pad: {args.week_of}
:orange_book: Big Accomplishments
:bulb: Learning & Insight
:information_source: Data Updates
:chart_with_upwards_trend: Visual
:loading: In Progress / Coming Up
🔗 Links/Resources to Read
""".strip()

    prompt_text = f"""STRUCTURE:
{report_structure}

TOPICS:
{args.topics}

DATA:
{args.data}
""".strip()

    # ----- CrewAI -----
    llm = LLM(model=args.model)

    agent = Agent(
        role="Writer",
        goal="Write a report based on data provided.",
        backstory="You are a data architect who provides weekly updates to the board",
        verbose=bool(args.verbose),
        llm=llm,
    )

    task = Task(
        description=(
            "Write a comprehensive weekly report following this structure:\n"
            "{report_structure}\n\n"
            "Cover these topics:\n"
            "{topics}\n\n"
            "Use the provided data: {data}"
        ),
        expected_output="A detailed weekly report following the specified structure",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=bool(args.verbose))

    # ----- MLflow -----
    mlflow.set_experiment(args.experiment)
    run_name = args.run_name or f"weekly_report_{args.week_of}"

    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()
    with mlflow.start_run(run_name=run_name):
        # Params & tags
        mlflow.log_param("week_of", args.week_of)
        mlflow.log_param("model", args.model)
        mlflow.log_param("secret_scope", args.secret_scope)
        mlflow.log_param("openai_key_name", args.openai_key_name)

        mlflow.set_tag("project", "weekly-report")
        mlflow.set_tag("prompt_version", args.prompt_version)

        # Execute
        result = crew.kickoff(
            inputs={
                "report_structure": report_structure,
                "topics": args.topics,
                "data": args.data,
            }
        )

        # Metrics
        elapsed = time.time() - start
        mlflow.log_metric("latency_seconds", elapsed)
        mlflow.log_metric("output_chars", len(str(result)))
        mlflow.log_metric("topics_chars", len(args.topics))
        mlflow.log_metric("data_chars", len(args.data))

        # Artifacts: prompt, inputs, output
        prompt_path = artifact_dir / "prompt.txt"
        prompt_path.write_text(prompt_text, encoding="utf-8")
        mlflow.log_artifact(str(prompt_path), artifact_path="prompts")

        inputs_path = artifact_dir / "inputs.json"
        inputs_path.write_text(
            json.dumps(
                {"report_structure": report_structure, "topics": args.topics, "data": args.data},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        mlflow.log_artifact(str(inputs_path), artifact_path="inputs")

        report_path = artifact_dir / "weekly_report.md"
        report_path.write_text(str(result), encoding="utf-8")
        mlflow.log_artifact(str(report_path), artifact_path="outputs")

    print(result)


if __name__ == "__main__":
    main()
