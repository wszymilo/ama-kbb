#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

import typer

from kbb.config import get_config
from kbb.crew import KbbFlow


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
        result = KbbFlow(rubric_path=rubric).kickoff(
            {
                "topic": topic,
                "current_year": current_year,
            }
        )
        print(result)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}
    try:
        KbbFlow().kickoff(inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        KbbFlow().kickoff(inputs={})

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}

    try:
        KbbFlow().kickoff(inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Please provide JSON payload as argument."
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": "",
    }

    try:
        result = KbbFlow().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
