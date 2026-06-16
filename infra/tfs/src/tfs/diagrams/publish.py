"""`tfs diagram-comment` — post (or update) the sticky PR comment for a diagram.

The image files are uploaded by GitHub's own ``actions/upload-artifact`` step; this
command just links that artifact into a sticky PR comment (no ``ci-diagrams``
branch, no git push). Runs only in CI; reads its context from the environment:

  GITHUB_REPOSITORY  owner/repo
  GITHUB_SHA         commit being diagrammed (optional, for display)
  GH_TOKEN           token with pull-requests:write (used by `gh`)
  GITHUB_REF / TFS_PR_NUMBER   to resolve the PR number (refs/pull/<n>/merge)

Pure helpers (marker / body / PR-number) are unit-tested; only the `gh` calls are
IO seams. Hard-fails (no silent skip) if required context is missing.
"""

from __future__ import annotations

import logging
import os
import re
import subprocess

log = logging.getLogger(__name__)


def _require(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(f"diagram-comment requires the {name} environment variable (CI context).")
    return val


def resolve_pr_number(ref: str | None = None, explicit: str | None = None) -> str:
    """PR number from TFS_PR_NUMBER, else parsed from GITHUB_REF (refs/pull/<n>/...)."""
    explicit = explicit if explicit is not None else os.environ.get("TFS_PR_NUMBER")
    if explicit:
        return explicit
    ref = ref if ref is not None else os.environ.get("GITHUB_REF", "")
    m = re.match(r"refs/pull/(\d+)/", ref)
    if not m:
        raise RuntimeError("Cannot resolve PR number from TFS_PR_NUMBER or GITHUB_REF (refs/pull/<n>/...).")
    return m.group(1)


def marker(stack: str) -> str:
    """The hidden HTML marker that makes the comment sticky (one per stack)."""
    return f"<!-- tf-diagram:{stack} -->"


def comment_body(stack: str, env: str, mode: str, artifact_url: str, sha: str = "") -> str:
    sha_note = f" (`{sha[:12]}`)" if sha else ""
    return "\n".join(
        [
            marker(stack),
            f"### \U0001f4ca `{stack}` — architecture {mode} ({env})",
            "",
            f"Rendered by `tfs diagram {stack} {env} --mode {mode}`. Nodes are coloured by category; "
            "in plan mode, borders mark create (+) / update (~) / replace (±) / delete (-).",
            "",
            f"**[⬇️ Download the diagram (SVG + PNG)]({artifact_url})** — workflow artifact{sha_note}.",
        ]
    )


def _gh(*args: str) -> str:  # pragma: no cover - subprocess IO seam (gh CLI)
    return subprocess.run(["gh", *args], check=True, text=True, capture_output=True).stdout


def _upsert_comment(repo: str, pr: str, mark: str, body: str) -> None:  # pragma: no cover - gh IO
    existing = _gh(
        "api", f"repos/{repo}/issues/{pr}/comments", "--paginate",
        "--jq", f'.[] | select(.body | contains("{mark}")) | .id',
    ).strip()
    if existing:
        cid = existing.splitlines()[0]
        _gh("api", "-X", "PATCH", f"repos/{repo}/issues/comments/{cid}", "-f", f"body={body}")
        log.info("updated sticky comment %s on PR #%s", cid, pr)
    else:
        _gh("api", f"repos/{repo}/issues/{pr}/comments", "-f", f"body={body}")
        log.info("created sticky comment on PR #%s", pr)


def post_comment(stack: str, env: str, mode: str, artifact_url: str) -> None:  # pragma: no cover - gh IO orchestration
    repo = _require("GITHUB_REPOSITORY")
    _require("GH_TOKEN")  # consumed by `gh`; presence-checked here for a clear error
    pr = resolve_pr_number()
    body = comment_body(stack, env, mode, artifact_url, os.environ.get("GITHUB_SHA", ""))
    _upsert_comment(repo, pr, marker(stack), body)
    log.info("✅ diagram comment posted to PR #%s", pr)
