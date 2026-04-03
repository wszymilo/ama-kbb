#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

import typer

from kbb.config import get_config
from kbb.crew import KbbWorkflow


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = typer.Typer()


@app.command()
def run(
    topic: str = typer.Option(..., "--topic", help="The research topic to explore"),
    rubric: str = typer.Option("", "--rubric", help="Path to rubric YAML file"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
    log_level: str = typer.Option("info", "--log-level", help="Set the logging level"),
    collection: str = typer.Option(None, "--collection", help="Specify the collection"),
    max_sources: int = typer.Option(
        5, "--max-sources", help="Maximum number of sources"
    ),
    current_year: str = typer.Option(
        str(datetime.now().year), "--current-year", help="Specify the current year"
    ),
):
    """
    Run the crew.
    """
    get_config()  # Validate config on startup

    if verbose:
        print(f"[DEBUG] Running with topic: {topic}")
        if rubric:
            print(f"[DEBUG] Using rubric: {rubric}")

    try:
        result = KbbWorkflow(rubric_path=rubric if rubric else "").run(
            topic=topic,
            current_year=str(current_year),
        )
        print(result)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}") from e


@app.command()
def train(
    topic: str = typer.Option("AI LLMs", "--topic", help="The research topic"),
    current_year: str = typer.Option(str(datetime.now().year), "--current-year"),
):
    """
    Train the crew for a given number of iterations.
    """
    try:
        KbbWorkflow().run(topic=topic, current_year=str(current_year))
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}") from e


@app.command()
def replay(
    topic: str = typer.Option("", "--topic", help="The research topic"),
    current_year: str = typer.Option(str(datetime.now().year), "--current-year"),
):
    """
    Replay the crew execution from a specific task.
    """
    try:
        KbbWorkflow().run(topic=topic, current_year=str(current_year))
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}") from e


@app.command()
def test(
    topic: str = typer.Option("AI LLMs", "--topic", help="The research topic"),
    current_year: str = typer.Option(str(datetime.now().year), "--current-year"),
):
    """
    Test the crew execution and returns the results.
    """
    try:
        KbbWorkflow().run(topic=topic, current_year=str(current_year))
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}") from e


@app.command()
def run_with_trigger(
    payload: str = typer.Option(..., "--payload", help="JSON payload"),
):
    """
    Run the crew with trigger payload.
    """
    import json

    try:
        trigger_payload = json.loads(payload)
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided")

    try:
        result = KbbWorkflow().run(topic="", current_year="")
        return result
    except Exception as e:
        raise Exception(
            f"An error occurred while running the crew with trigger: {e}"
        ) from e


if __name__ == "__main__":
    app()
