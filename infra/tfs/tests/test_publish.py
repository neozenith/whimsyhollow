"""Pure helpers of the diagram-comment publisher (no gh/network — those are the
pragma'd IO seams). Marker stickiness, comment body, PR-number resolution, env guard."""

from __future__ import annotations

import pytest

from tfs.diagrams import publish


def test_marker_is_stack_scoped():
    assert publish.marker("webapp") == "<!-- tf-diagram:webapp -->"
    assert publish.marker("webapp") != publish.marker("monitoring")


def test_comment_body_links_artifact_and_is_sticky():
    url = "https://github.com/o/r/actions/runs/1/artifacts/42"
    body = publish.comment_body("webapp", "dev", "plan", url, sha="abcdef1234567890")
    assert body.startswith(publish.marker("webapp"))  # sticky marker first
    assert url in body
    assert "webapp" in body and "dev" in body and "plan" in body
    assert "abcdef123456" in body  # sha truncated to 12
    assert "Download" in body


def test_comment_body_without_sha():
    body = publish.comment_body("s", "prod", "state", "http://x")
    assert "()" not in body  # no empty sha parens
    assert "http://x" in body


@pytest.mark.parametrize(
    "explicit,ref,expected",
    [
        ("123", "refs/pull/999/merge", "123"),  # explicit wins
        (None, "refs/pull/77/merge", "77"),  # parsed from ref
        (None, "refs/pull/5/head", "5"),
    ],
)
def test_resolve_pr_number(explicit, ref, expected):
    assert publish.resolve_pr_number(ref=ref, explicit=explicit) == expected


def test_resolve_pr_number_unresolvable_raises():
    with pytest.raises(RuntimeError, match="PR number"):
        publish.resolve_pr_number(ref="refs/heads/main", explicit="")


def test_require_env(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="GH_TOKEN"):
        publish._require("GH_TOKEN")
    monkeypatch.setenv("GH_TOKEN", "tok")
    assert publish._require("GH_TOKEN") == "tok"
