"""Typer CLI entry point: ``python -m apitester run <collection> --env <name>``."""
from __future__ import annotations

from pathlib import Path

import typer

from apitester.loader import load_collection, load_environment
from apitester.reporter import export_json, print_report
from apitester.runner import run_collection

app = typer.Typer(add_completion=False, help="Declarative HTTP API tester")


@app.callback()
def _main() -> None:
    """Keep `run` as an explicit sub-command (multi-command mode)."""


@app.command()
def run(
    collection: Path = typer.Argument(..., help="Path to a YAML collection file"),
    env: str = typer.Option("prod", "--env", "-e", help="Environment name"),
    env_file: Path = typer.Option(
        Path("collections/environments.yaml"), "--env-file", help="Environments file"
    ),
    report: Path = typer.Option(
        Path("report/result.json"), "--report", help="Where to write the JSON report"
    ),
    timeout: float = typer.Option(30.0, "--timeout", help="Per-request timeout in seconds"),
) -> None:
    """Run a collection and exit non-zero if any request fails (CI gate)."""
    variables = load_environment(env_file, env)
    coll = load_collection(collection)
    results = run_collection(coll, variables, timeout=timeout)

    print_report(coll.name, results)
    export_json(report, coll.name, results)

    failed = sum(1 for r in results if not r.passed)
    raise typer.Exit(code=1 if failed else 0)


if __name__ == "__main__":
    app()
