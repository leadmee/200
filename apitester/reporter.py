"""Console (rich) and JSON reporting for runner results."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from apitester.runner import RequestResult

_console = Console()


def print_report(collection_name: str, results: list[RequestResult]) -> None:
    table = Table(title=f"API Tester — {collection_name}", header_style="bold white on blue")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Request")
    table.add_column("Method", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Time", justify="right")
    table.add_column("Result", justify="center")
    table.add_column("Details")

    for idx, res in enumerate(results, start=1):
        if res.error:
            details = f"[red]ERROR: {res.error}[/red]"
        else:
            failed = [c for c in res.checks if not c.passed]
            details = (
                "; ".join(f"{c.name}: {c.detail}" for c in failed)
                if failed
                else "; ".join(c.name for c in res.checks) or "no assertions"
            )
        verdict = "[green]PASS[/green]" if res.passed else "[red]FAIL[/red]"
        table.add_row(
            str(idx),
            res.name,
            res.method,
            str(res.status if res.status is not None else "-"),
            f"{res.elapsed_ms:.0f} ms",
            verdict,
            details,
        )

    _console.print(table)
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    style = "bold green" if passed == total else "bold red"
    _console.print(f"[{style}]{passed}/{total} requests passed[/{style}]")


def export_json(report_path: str | Path, collection_name: str, results: list[RequestResult]) -> None:
    payload = {
        "collection": collection_name,
        "total": len(results),
        "passed": sum(1 for r in results if r.passed),
        "results": [
            {
                "name": r.name,
                "method": r.method,
                "url": r.url,
                "status": r.status,
                "elapsed_ms": round(r.elapsed_ms, 1),
                "passed": r.passed,
                "error": r.error,
                "checks": [asdict(c) for c in r.checks],
            }
            for r in results
        ],
    }
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
