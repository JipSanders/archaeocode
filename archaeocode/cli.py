from __future__ import annotations

import click

from . import __version__
from .display import (
    console,
    display_ancient_files,
    display_carbon_date,
    display_file_history,
    display_survey,
    make_progress,
)
from .git_ops import (
    find_repo,
    get_all_file_ages,
    get_ancient_files,
    get_file_history,
    get_line_ages,
    get_tree_files,
    resolve_file_path,
)


@click.group()
@click.version_option(__version__, prog_name="archaeocode")
def cli():
    """Archaeocode — Excavate the ancient history buried in any git repository."""


@cli.command()
@click.option("--path", "-p", default=".", show_default=True, help="Repository path.")
@click.option("--limit", "-n", default=20, show_default=True, help="Number of files to show.")
@click.option("--min-age", type=int, default=None, metavar="DAYS", help="Only include files untouched for at least DAYS.")
def dig(path: str, limit: int, min_age: int | None) -> None:
    """Find the most ancient, untouched files in the repository.

    Scans all tracked files and ranks them by how long since they were last
    touched. Ancient files are candidates for dead code, forgotten APIs, or
    buried history.
    """
    repo = find_repo(path)
    total = len(get_tree_files(repo))
    progress = make_progress("Digging through the layers…", total=total)
    task_id = progress.task_ids[0]
    with progress:
        files = get_ancient_files(
            repo,
            limit=limit,
            min_age_days=min_age,
            on_progress=lambda _: progress.advance(task_id),
        )
    display_ancient_files(files)


@cli.command()
@click.argument("file_path")
@click.option("--path", "-p", default=".", show_default=True, help="Repository path.")
@click.option("--limit", "-n", default=15, show_default=True, help="Number of commits to show.")
def excavate(file_path: str, path: str, limit: int) -> None:
    """Excavate the commit history of FILE, layer by layer.

    Shows the commit history for a specific file with change statistics
    and temporal context, from most recent to oldest.
    """
    repo = find_repo(path)
    resolved = resolve_file_path(repo, file_path)
    history = get_file_history(repo, resolved, limit=limit)
    display_file_history(resolved, history)


@cli.command("carbon-date")
@click.argument("file_path")
@click.option("--path", "-p", default=".", show_default=True, help="Repository path.")
def carbon_date(file_path: str, path: str) -> None:
    """Carbon-date the lines of FILE to reveal how old each line is.

    Uses git blame to annotate each line with the age of the last commit
    that modified it. Lines are color-coded: green (recent) → red (ancient).
    """
    repo = find_repo(path)
    resolved = resolve_file_path(repo, file_path)
    with console.status("[dim]Calculating ages...[/dim]"):
        lines = get_line_ages(repo, resolved)
    display_carbon_date(resolved, lines)


@cli.command()
@click.option("--path", "-p", default=".", show_default=True, help="Repository path.")
def survey(path: str) -> None:
    """Survey the age distribution of the entire repository.

    Shows a histogram of how recently each file was last modified,
    giving a high-level overview of the repository's age profile.
    """
    repo = find_repo(path)
    total = len(get_tree_files(repo))
    progress = make_progress("Surveying the dig site…", total=total)
    task_id = progress.task_ids[0]
    with progress:
        files = get_all_file_ages(repo, on_progress=lambda _: progress.advance(task_id))
    display_survey(repo.working_dir, files)
