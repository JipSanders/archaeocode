from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click
from git import GitCommandError, InvalidGitRepositoryError, Repo


def find_repo(path: str) -> Repo:
    try:
        return Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise click.ClickException(f"No git repository found at or above '{path}'")


def resolve_file_path(repo: Repo, file_path: str) -> str:
    """Convert an absolute or CWD-relative path to a repo-root-relative path."""
    p = Path(file_path).resolve()
    try:
        return str(p.relative_to(Path(repo.working_dir).resolve()))
    except ValueError:
        return file_path


def get_tree_files(repo: Repo) -> list[str]:
    try:
        return [item.path for item in repo.tree().traverse() if item.type == "blob"]
    except Exception as e:
        raise click.ClickException(f"Failed to read repository tree: {e}")


def get_all_file_ages(
    repo: Repo,
    on_progress: "callable[[str], None] | None" = None,
) -> list[dict]:
    """Return age data for every tracked file. Caller slices/filters as needed."""
    now = datetime.now(timezone.utc)
    tree_files = get_tree_files(repo)
    results = []
    for file_path in tree_files:
        if on_progress:
            on_progress(file_path)
        try:
            commits = list(repo.iter_commits(paths=file_path, max_count=1))
            if not commits:
                continue
            c = commits[0]
            last_modified = c.committed_datetime
            age_days = (now - last_modified).days
            results.append(
                {
                    "path": file_path,
                    "last_modified": last_modified,
                    "age_days": age_days,
                    "last_author": c.author.name,
                    "last_message": c.message.strip().splitlines()[0],
                }
            )
        except Exception:
            continue
    return results


def get_ancient_files(
    repo: Repo,
    limit: int = 20,
    min_age_days: int | None = None,
    on_progress: "callable[[str], None] | None" = None,
) -> list[dict]:
    results = get_all_file_ages(repo, on_progress=on_progress)
    if min_age_days is not None:
        results = [f for f in results if f["age_days"] >= min_age_days]
    results.sort(key=lambda x: x["age_days"], reverse=True)
    return results[:limit]


def get_file_history(repo: Repo, file_path: str, limit: int = 15) -> list[dict]:
    results = []
    for c in repo.iter_commits(paths=file_path, max_count=limit):
        stats = c.stats.files.get(file_path, {})
        results.append(
            {
                "sha": c.hexsha[:8],
                "date": c.committed_datetime,
                "author": c.author.name,
                "message": c.message.strip().splitlines()[0],
                "insertions": stats.get("insertions", 0),
                "deletions": stats.get("deletions", 0),
            }
        )
    return results


def get_line_ages(repo: Repo, file_path: str) -> list[dict]:
    now = datetime.now(timezone.utc)
    try:
        blame = repo.blame("HEAD", file_path)
    except GitCommandError as e:
        raise click.ClickException(f"git blame failed for '{file_path}': {e}")

    lines = []
    for commit, line_contents in blame:
        date = commit.committed_datetime
        age_days = (now - date).days
        for content in line_contents:
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
            lines.append(
                {
                    "sha": commit.hexsha[:8],
                    "author": commit.author.name,
                    "date": date,
                    "age_days": age_days,
                    "content": content,
                }
            )
    return lines
