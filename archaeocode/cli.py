from __future__ import annotations

import click

from . import __version__
from .display import (
    console,
    display_ancient_files,
    display_carbon_date,
    display_churn,
    display_file_history,
    display_header,
    display_survey,
    make_progress,
)
from .git_ops import (
    find_repo,
    get_all_file_ages,
    get_ancient_files,
    get_churn,
    get_file_history,
    get_line_ages,
    get_repo_info,
    get_tree_files,
    resolve_file_path,
)


@click.group()
@click.version_option(__version__, prog_name="arc")
def cli():
    """arc — Unearth the history buried in any git repository.

    Every codebase has layers. arc reads them.
    """


@cli.command()
@click.option("--path", "-p", default=".", show_default=True, help="Repository path or GitHub URL.")
@click.option("--limit", "-n", default=20, show_default=True, help="Number of files to surface.")
@click.option("--min-age", type=int, default=None, metavar="DAYS", help="Only surface files untouched for at least DAYS.")
def dig(path: str, limit: int, min_age: int | None) -> None:
    """Unearth the oldest, most untouched files in the repository.

    Ranks every tracked file by how long it has gone untouched.
    Ancient files are candidates for dead code, forgotten APIs,
    and buried history nobody remembers writing.
    """
    repo = find_repo(path)
    display_header("DIG", get_repo_info(repo))
    total = len(get_tree_files(repo))
    progress = make_progress("Brushing away the sediment…", total=total)
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
@click.option("--path", "-p", default=".", show_default=True, help="Repository path or GitHub URL.")
@click.option("--limit", "-n", default=15, show_default=True, help="Number of strata to expose.")
def excavate(file_path: str, path: str, limit: int) -> None:
    """Excavate FILE's history, stratum by stratum.

    Exposes every commit that touched this file, from the most recent
    surface layer down to the original deposit — with diff bars showing
    the scale of each change at a glance.
    """
    repo = find_repo(path)
    display_header("EXCAVATE", get_repo_info(repo))
    resolved = resolve_file_path(repo, file_path)
    history = get_file_history(repo, resolved, limit=limit)
    display_file_history(resolved, history)


@cli.command("carbon-date")
@click.argument("file_path")
@click.option("--path", "-p", default=".", show_default=True, help="Repository path or GitHub URL.")
def carbon_date(file_path: str, path: str) -> None:
    """Determine the age of every line in FILE.

    Runs isotope analysis on each line — annotating it with the age
    of the commit that last touched it. Green means fresh. Red means
    this code predates anyone on the current team.
    """
    repo = find_repo(path)
    display_header("CARBON DATE", get_repo_info(repo))
    resolved = resolve_file_path(repo, file_path)
    with console.status("[dim]Running isotope analysis…[/dim]"):
        lines = get_line_ages(repo, resolved)
    display_carbon_date(resolved, lines)


@cli.command()
@click.option("--path", "-p", default=".", show_default=True, help="Repository path or GitHub URL.")
@click.option("--limit", "-n", default=20, show_default=True, help="Number of files to surface.")
def churn(path: str, limit: int) -> None:
    """Find the most unstable ground in the repository.

    Reads the full geological record to rank files by how many times
    they have been disturbed. High churn means contested terrain or
    code that never quite settled. Low churn is bedrock.
    """
    repo = find_repo(path)
    display_header("CHURN", get_repo_info(repo))
    try:
        total_commits = int(repo.git.rev_list("--count", "HEAD"))
    except Exception:
        total_commits = 0
    progress = make_progress("Reading the geological record…", total=total_commits)
    task_id = progress.task_ids[0]
    with progress:
        files = get_churn(repo, limit=limit, on_progress=lambda _: progress.advance(task_id))
    display_churn(files)


@cli.command()
@click.option("--path", "-p", default=".", show_default=True, help="Repository path or GitHub URL.")
def survey(path: str) -> None:
    """Map the age profile of the entire dig site.

    A histogram of when files were last disturbed — from fresh surface
    finds to deep strata untouched for years. Run this first on any
    unfamiliar repository.
    """
    repo = find_repo(path)
    display_header("SURVEY", get_repo_info(repo))
    total = len(get_tree_files(repo))
    progress = make_progress("Mapping the dig site…", total=total)
    task_id = progress.task_ids[0]
    with progress:
        files = get_all_file_ages(repo, on_progress=lambda _: progress.advance(task_id))
    display_survey(repo.working_dir, files)
