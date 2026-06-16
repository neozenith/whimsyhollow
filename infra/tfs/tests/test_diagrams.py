"""Tests for the diagram pure-logic core: plan parsing, classification, layout,
the draw.io model, and the SVG render. All offline against a committed plan
fixture — no terraform/gcloud/cairo.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tfs.diagrams import drawio_model, layout, plan_model, registry, stencils, svg_render

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "plan.json").read_text())


# --- registry (the cloud-agnostic classification seam) ------------------------


@pytest.mark.parametrize(
    "tf_type,expected",
    [
        ("google_storage_bucket_iam_member", True),
        ("google_project_iam_member", True),
        ("google_bigquery_dataset_iam_member", True),
        ("aws_iam_policy", True),  # cloud-neutral: matches _iam_policy across providers
        ("aws_s3_bucket_policy", False),  # precision: a plain _policy is NOT an IAM grant
        ("google_cloud_run_v2_service", False),
        ("google_service_account", False),
    ],
)
def test_is_iam_grant(tf_type, expected):
    assert registry.is_iam_grant(tf_type) is expected


def test_skip_and_identity_and_color():
    assert registry.is_skipped("google_project_service")
    assert not registry.is_skipped("google_storage_bucket")
    assert registry.is_identity("google_service_account")
    assert not registry.is_identity("google_storage_bucket")
    assert registry.category_for("google_cloud_run_v2_service") == "Compute"
    assert registry.category_for("totally_unknown_type") == "Other"
    assert registry.color_for("google_storage_bucket") == registry.CATEGORY_COLOR["Storage"]


# --- stencils (vendored asset) ------------------------------------------------


def test_every_registered_stencil_is_vendored():
    for stencil_id, _category in registry.RESOURCE_STENCILS.values():
        s = stencils.get(stencil_id)
        assert s is not None, f"{stencil_id} missing from stencils.json"
        assert s.w > 0 and s.h > 0
        assert "currentColor" in s.svg  # themeable placeholder present
        assert s.stencil_b64  # draw.io inline payload present


def test_stencil_get_unknown_is_none():
    assert stencils.get("mxgraph.nope/Nothing") is None
    assert stencils.get(None) is None


def test_raster_module_imports_without_cairo():
    # cairosvg is imported lazily inside the call, so the module loads even where the
    # system cairo library is absent (e.g. `tfs diagram --help`). The call itself is
    # the IO seam (pragma'd) and is exercised by live CI runs.
    from tfs.diagrams import raster

    assert callable(raster.svg_to_png)


# --- comprehensive multi-cloud registry --------------------------------------


@pytest.mark.parametrize(
    "tf_type,expected_lib,expected_category",
    [
        ("aws_lambda_function", "mxgraph.aws4", "Compute"),
        ("aws_s3_bucket", "mxgraph.aws4", "Storage"),
        ("azurerm_linux_function_app", "mxgraph.mscae.cloud", "Compute"),
        ("azurerm_cosmosdb_account", "mxgraph.mscae.cloud", "Data"),
        ("kubernetes_deployment", "mxgraph.kubernetes2", "Compute"),
        ("google_pubsub_topic", "mxgraph.gcp2", "Messaging"),
    ],
)
def test_multicloud_mappings_resolve(tf_type, expected_lib, expected_category):
    sid, category = registry.stencil_for(tf_type)
    assert sid is not None and sid.startswith(expected_lib + "/")
    assert category == expected_category
    assert stencils.get(sid) is not None  # the icon is actually vendored


def test_registry_covers_all_four_providers():
    for prefix in ("google_", "aws_", "azurerm_", "kubernetes_"):
        assert any(k.startswith(prefix) for k in registry.RESOURCE_STENCILS), prefix
    assert len(registry.RESOURCE_STENCILS) >= 150
    # every category used by the registry has an accent colour
    for _sid, category in registry.RESOURCE_STENCILS.values():
        assert category in registry.CATEGORY_COLOR


def test_multicloud_iam_identities():
    assert registry.is_identity("aws_iam_role")
    assert registry.is_identity("kubernetes_service_account")
    assert registry.is_iam_grant("aws_iam_role_policy_attachment") is False  # _attachment, not a binding
    assert registry.is_iam_grant("azurerm_role_assignment") is False  # not _iam_*


# --- plan_model ---------------------------------------------------------------


def test_build_graph_state_filters_noise():
    g = plan_model.build_graph(FIXTURE, mode="state", iam="edges")
    ids = set(g.nodes)
    assert "google_project_service.run" not in ids  # skipped
    assert "data.google_project.this" not in ids  # data source
    assert "google_storage_bucket_iam_member.runtime_object_admin" not in ids  # iam -> edge
    assert "google_cloud_run_v2_service.app" in ids
    assert "terraform_data.image" in ids  # unmapped -> rendered as a plain box
    assert len(g.nodes) == 8


def test_iam_grants_become_dashed_role_edges():
    g = plan_model.build_graph(FIXTURE, mode="state", iam="edges")
    iam = [e for e in g.edges if e.dashed]
    assert any(
        e.src == "google_service_account.runtime"
        and e.dst == "google_storage_bucket.assets"
        and e.label == "storage.objectAdmin"
        for e in iam
    )
    # project_iam_member references only the SA (no non-identity target) -> no edge
    assert all(e.dst != "google_project_iam_member.runtime_datastore_user" for e in g.edges)


def test_iam_nodes_mode_renders_grants_as_boxes():
    g = plan_model.build_graph(FIXTURE, mode="state", iam="nodes")
    assert "google_storage_bucket_iam_member.runtime_object_admin" in g.nodes
    assert not any(e.dashed for e in g.edges)


def test_reference_edges_have_no_self_loops_or_dupes():
    g = plan_model.build_graph(FIXTURE, mode="state", iam="edges")
    refs = [(e.src, e.dst) for e in g.edges if not e.dashed]
    assert all(s != d for s, d in refs)
    assert len(refs) == len(set(refs))
    assert ("google_cloud_run_v2_service.app", "google_service_account.runtime") in refs


def test_plan_mode_carries_actions():
    g = plan_model.build_graph(FIXTURE, mode="plan", iam="edges")
    fs = g.nodes["google_firestore_database.app"]
    assert fs.actions == ("create", "delete")
    assert fs.action_style()[0] == "±"
    cr = g.nodes["google_cloud_run_v2_service.app"]
    assert cr.action_style()[0] == "~"


def test_base_address_strips_index():
    assert plan_model.base_address('google_x.y["k"]') == "google_x.y"
    assert plan_model.base_address("google_x.y[0]") == "google_x.y"


# --- layout -------------------------------------------------------------------


def test_layout_is_deterministic_and_bounded():
    g = plan_model.build_graph(FIXTURE, mode="state", iam="edges")
    a = layout.compute(g)
    b = layout.compute(g)
    assert a.nodes == b.nodes and a.clusters == b.clusters
    assert a.width > 0 and a.height > 0
    assert set(a.nodes) == set(g.nodes)
    assert "Compute" in a.clusters and "Data" in a.clusters


# --- drawio model + svg -------------------------------------------------------


def test_mxfile_has_a_cell_per_node_and_inline_stencils():
    g = plan_model.build_graph(FIXTURE, mode="state", iam="edges")
    lay = layout.compute(g)
    mx = drawio_model.build_mxfile(g, lay, title="t")
    assert mx.startswith("<mxfile") and "<mxGraphModel" in mx
    assert mx.count('vertex="1"') == len(g.nodes)
    assert "shape=stencil(" in mx  # mapped nodes embed inline stencils


def test_render_is_drawio_compatible_svg():
    g = plan_model.build_graph(FIXTURE, mode="state", iam="edges")
    lay = layout.compute(g)
    svg = svg_render.render(g, lay, title="webapp | dev | state", mode="state")
    assert svg.startswith("<svg") and "content=" in svg
    # the editable draw.io model is embedded (HTML-escaped) in the content attribute
    assert "&lt;mxfile" in svg and "mxGraphModel" in svg
    assert "Compute" in svg and "cloud_run_v2_service" in svg


def test_plan_mode_adds_legend_state_mode_does_not():
    g = plan_model.build_graph(FIXTURE, mode="plan", iam="edges")
    lay = layout.compute(g)
    assert "+ create" in svg_render.render(g, lay, title="t", mode="plan")
    g2 = plan_model.build_graph(FIXTURE, mode="state", iam="edges")
    assert "+ create" not in svg_render.render(g2, layout.compute(g2), title="t", mode="state")
