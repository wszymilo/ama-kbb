#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

import typer

from kbb.config import get_config
from kbb.crew import Kbb


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = typer.Typer()

@app.command()
def run(
    topic: str = typer.Option(..., "--topic"),
    verbose: bool = typer.Option(False, "--verbose"),
    log_level: str = typer.Option("info", "--log-level"),
    collection: str = typer.Option(None, "--collection"),
    max_sources: int = typer.Option(5, "--max-sources"),
    rubric: str = typer.Option(None, "--rubric"),
    current_year: str = typer.Option(str(datetime.now().year), "--current-year")
):
    """
    Run the crew.
    """
    get_config()  # Validate config on startup

    inputs = {
        "topic": topic,
        "verbose": verbose,
        "log_level": log_level,
        "collection": collection,
        "max_sources": max_sources,
        "rubric": rubric,
        "current_year": current_year,
    }

    if verbose:
        print(f"[DEBUG] Running with inputs: {inputs}")

    inputs = {"topic": topic, "current_year": current_year}

    try:
        Kbb().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}
    try:
        Kbb().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Kbb().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}

    try:
        Kbb().crew().test(
            n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs
        )

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
        result = Kbb().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
