from __future__ import annotations

from datetime import datetime, timezone

from rich import box
from rich.bar import Bar
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()

_BUCKETS = [
    ("< 1 week",   0,   7),
    ("< 1 month",  7,   30),
    ("< 3 months", 30,  90),
    ("< 6 months", 90,  180),
    ("< 1 year",   180, 365),
    ("1 – 2 years", 365, 730),
    ("2 + years",  730, None),
]


def make_progress(description: str = "Scanning…", total: int = 0) -> Progress:
    p = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        transient=True,
        console=console,
    )
    p.add_task(description, total=total)
    return p


def _age_color(age_days: int) -> str:
    if age_days < 30:
        return "bright_green"
    if age_days < 90:
        return "green"
    if age_days < 180:
        return "yellow"
    if age_days < 365:
        return "orange3"
    if age_days < 730:
        return "red"
    return "bright_red"


def _age_label(age_days: int) -> str:
    if age_days < 1:
        return "today"
    if age_days < 7:
        return f"{age_days}d"
    if age_days < 30:
        return f"{age_days // 7}w"
    if age_days < 365:
        return f"{age_days // 30}mo"
    years = age_days // 365
    months = (age_days % 365) // 30
    return f"{years}y {months}mo" if months else f"{years}y"


def display_ancient_files(files: list[dict]) -> None:
    if not files:
        console.print("[yellow]No files found matching criteria.[/yellow]")
        return

    table = Table(
        title="[bold]Ancient Files[/bold]  —  Oldest untouched code in the repository",
        box=box.ROUNDED,
        header_style="bold cyan",
        expand=True,
    )
    table.add_column("Age", justify="right", width=7, no_wrap=True)
    table.add_column("File", style="cyan", no_wrap=True, ratio=2)
    table.add_column("Last Author", style="dim", max_width=14, no_wrap=True)
    table.add_column("Last Commit", style="dim", no_wrap=True, ratio=3)
    table.add_column("Date", style="dim", min_width=10, no_wrap=True)

    for f in files:
        age_days = f["age_days"]
        color = _age_color(age_days)
        label = _age_label(age_days)
        table.add_row(
            Text(label, style=f"bold {color}"),
            escape(f["path"]),
            escape(f["last_author"]),
            escape(f["last_message"][:55]),
            f["last_modified"].strftime("%Y-%m-%d"),
        )

    console.print(table)
    console.print()


def display_file_history(file_path: str, history: list[dict]) -> None:
    if not history:
        console.print(f"[yellow]No history found for '{escape(file_path)}'[/yellow]")
        return

    now = datetime.now(timezone.utc)
    console.print()
    console.print(
        Panel(
            f"[bold cyan]{escape(file_path)}[/bold cyan]",
            title="[bold]Excavation Report[/bold]",
            subtitle=f"[dim]{len(history)} commits[/dim]",
            border_style="cyan",
        )
    )

    for i, c in enumerate(history):
        age_days = (now - c["date"]).days
        color = _age_color(age_days)
        age = _age_label(age_days)

        ins, dels = c["insertions"], c["deletions"]
        diff = f"  [green]+{ins}[/green] [red]-{dels}[/red]" if (ins or dels) else ""

        marker = "◆" if i == 0 else "◇"
        console.print(
            f"  [{color}]{marker}[/{color}] "
            f"[dim]{c['sha']}[/dim]  "
            f"[bold]{escape(c['message'][:60])}[/bold]"
            f"{diff}"
        )
        console.print(
            f"    [dim]{escape(c['author'])} · "
            f"{c['date'].strftime('%Y-%m-%d %H:%M')} · "
            f"[{color}]{age}[/{color}][/dim]"
        )
        if i < len(history) - 1:
            console.print("    [dim]│[/dim]")

    console.print()


def display_carbon_date(file_path: str, lines: list[dict]) -> None:
    if not lines:
        console.print(f"[yellow]No blame data for '{escape(file_path)}'[/yellow]")
        return

    console.print()
    console.print(
        Panel(
            f"[bold cyan]{escape(file_path)}[/bold cyan]",
            title="[bold]Carbon Dating[/bold]",
            subtitle=f"[dim]{len(lines)} lines[/dim]",
            border_style="magenta",
        )
    )

    legend = Text("  Age key: ")
    for label, color in [
        ("<1mo", "bright_green"),
        ("<3mo", "green"),
        ("<6mo", "yellow"),
        ("<1yr", "orange3"),
        ("<2yr", "red"),
        ("2yr+", "bright_red"),
    ]:
        legend.append("█ ", style=color)
        legend.append(f"{label}  ", style="dim")
    console.print(legend)
    console.print()

    prev_sha = None
    for i, line in enumerate(lines, 1):
        age_days = line["age_days"]
        color = _age_color(age_days)
        sha = line["sha"]
        content = line["content"].rstrip("\n")

        row = Text()
        row.append(f"{i:>4} ", style="dim")

        if sha != prev_sha:
            age = _age_label(age_days)
            author = line["author"][:13]
            row.append(sha, style=f"{color} dim")
            row.append(f" {age:>5} ", style=color)
            row.append(f"{author:<13}", style="dim")
            prev_sha = sha
        else:
            row.append(" " * 27, style="dim")

        row.append(" │ ", style="dim")
        row.append(content[:120], style=color)
        console.print(row)

    console.print()


def display_survey(repo_path: str, files: list[dict]) -> None:
    if not files:
        console.print("[yellow]No tracked files found.[/yellow]")
        return

    total = len(files)
    oldest = max(files, key=lambda f: f["age_days"])
    newest = min(files, key=lambda f: f["age_days"])

    console.print()
    console.print(
        Panel(
            f"[bold]{escape(repo_path)}[/bold]",
            title="[bold]Repository Survey[/bold]",
            subtitle=f"[dim]{total} tracked files[/dim]",
            border_style="cyan",
        )
    )

    bar_width = 40
    for label, lo, hi in _BUCKETS:
        hi_val = hi if hi is not None else float("inf")
        count = sum(1 for f in files if lo <= f["age_days"] < hi_val)
        pct = count / total * 100 if total else 0
        filled = round(pct / 100 * bar_width)
        color = _age_color(lo)
        bar = "█" * filled + "░" * (bar_width - filled)
        console.print(
            f"  [{color}]{label:<13}[/{color}]  [{color}]{bar}[/{color}]"
            f"  [dim]{count:>4} files  {pct:>5.1f}%[/dim]"
        )

    console.print()
    console.print(
        f"  [dim]Oldest:[/dim] [{_age_color(oldest['age_days'])}]{escape(oldest['path'])}[/]"
        f"  [dim]({_age_label(oldest['age_days'])} ago)[/dim]"
    )
    console.print(
        f"  [dim]Newest:[/dim] [{_age_color(newest['age_days'])}]{escape(newest['path'])}[/]"
        f"  [dim]({_age_label(newest['age_days'])} ago)[/dim]"
    )
    console.print()
