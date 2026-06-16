"""`tfs diagram <stack> <env>` entry point.

Orchestrates: throwaway plan -> plan JSON -> graph -> layout -> draw.io-compatible
SVG (+ PNG). Drives Terraform through the shared :mod:`tfs._terraform` driver, so
the diagram's plan can't diverge from `tfs plan`. With ``--publish`` it pushes the
result to a PR (CI only).
"""

from __future__ import annotations

import json
import logging
from argparse import Namespace
from pathlib import Path

from tfs import _terraform as tf
from tfs.config import list_stacks
from tfs.diagrams import layout as layout_mod
from tfs.diagrams import plan_model, svg_render
from tfs.errors import TFStackCLIInputError
from tfs.gcp import check_project
from tfs.roots import find_infra_root

log = logging.getLogger(__name__)

_PLAN_FILE = "tmp/diagram.tfplan"


def _load_plan_json(stack: str, env: str, infra_root: Path) -> dict:  # pragma: no cover - terraform subprocess IO
    """init + (throwaway, unlocked) plan -> the plan JSON document."""
    stack_path = infra_root / "stacks" / stack
    (stack_path / "tmp").mkdir(parents=True, exist_ok=True)
    var_file = tf.tfvars_flag(stack_path, env)

    log.info("Planning %s/%s for diagram …", stack, env)
    tf.run(tf.init_cmd(stack, env), infra_root, capture=True)
    tf.run(tf.plan_cmd(stack, env, var_file, lock=False, out=_PLAN_FILE), infra_root, capture=True)
    out = tf.run(tf.show_json_cmd(stack, _PLAN_FILE), infra_root, capture=True)
    return json.loads(out.stdout)


def cmd_diagram(args: Namespace) -> None:  # pragma: no cover - terraform/cairo IO orchestration
    infra_root = find_infra_root(override=args.infra_root)
    if args.stack not in list_stacks(infra_root):
        raise TFStackCLIInputError(f"Stack '{args.stack}' does not exist. One of {list_stacks(infra_root)}")
    check_project(args.env)

    doc = _load_plan_json(args.stack, args.env, infra_root)
    graph = plan_model.build_graph(doc, mode=args.mode, iam=args.iam)
    layout = layout_mod.compute(graph)
    title = f"{args.stack} | {args.env} | {args.mode}"
    svg = svg_render.render(graph, layout, title=title, mode=args.mode)

    out_dir = Path(args.out_dir) if getattr(args, "out_dir", None) else infra_root / "diagrams"
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / f"{args.stack}-{args.env}-{args.mode}"
    svg_path = base.with_suffix(".svg")
    png_path = base.with_suffix(".png")
    svg_path.write_text(svg, encoding="utf-8")

    # Rasterize to PNG. Imported lazily so a missing system cairo only bites the
    # PNG step (and crashes loudly there), never `tfs diagram --help` etc.
    from tfs.diagrams import raster

    raster.svg_to_png(svg_path, png_path)
    log.info("✅ wrote %s (+ .png) — %d resources", svg_path.name, len(graph.nodes))


def cmd_diagram_comment(args: Namespace) -> None:  # pragma: no cover - gh subprocess IO
    """Post/update the sticky PR comment linking to the uploaded diagram artifact.

    No terraform/render/cloud access — the image files are produced by `tfs diagram`
    and uploaded by GitHub's actions/upload-artifact; this only links that artifact
    URL into the PR comment. CI-only (reads GH context from the environment)."""
    from tfs.diagrams import publish

    publish.post_comment(args.stack, args.env, args.mode, args.artifact_url)
