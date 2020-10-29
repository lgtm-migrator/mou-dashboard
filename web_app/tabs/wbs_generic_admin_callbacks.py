"""Admin-only callbacks for a specified WBS layout."""


import logging
from typing import Dict, List, Optional, Tuple

import dash_bootstrap_components as dbc  # type: ignore[import]
import dash_core_components as dcc  # type: ignore[import]
from dash.dependencies import Input, Output, State  # type: ignore[import]
from flask_login import current_user  # type: ignore[import]

from ..config import app
from ..data_source import data_source as src
from ..data_source import table_config as tc
from ..data_source.utils import DataSourceException
from ..utils import dash_utils as du
from ..utils import types


def _get_upload_success_modal_body(
    filename: str,
    n_records: int,
    prev_snap: Optional[types.SnapshotInfo],
    curr_snap: Optional[types.SnapshotInfo],
) -> List[dcc.Markdown]:
    """Make the message for the ingest confirmation toast."""

    def _pseudonym(_snap: types.SnapshotInfo) -> str:
        if _snap["name"]:
            return f"\"{_snap['name']}\""
        return du.get_human_time(_snap["timestamp"])

    body: List[dcc.Markdown] = [
        dcc.Markdown(f'Uploaded {n_records} records from "{filename}".'),
        dcc.Markdown("A snapshot was made of:"),
    ]

    if prev_snap:
        body.append(dcc.Markdown(f"- the previous table ({_pseudonym(prev_snap)}) and"))
    if curr_snap:
        body.append(dcc.Markdown(f"- the current table ({_pseudonym(curr_snap)})"))

    return body


@app.callback(  # type: ignore[misc]
    Output("refresh-for-override-success", "run"),
    [Input("wbs-upload-success-view-new-table-button", "n_clicks")],  # user-only
    prevent_initial_call=True,
)
def refresh_for_override_success(_: int) -> str:
    """Refresh page for to view new live table."""
    return "location.reload();"


@app.callback(  # type: ignore[misc]
    [
        Output("wbs-upload-xlsx-modal", "is_open"),
        Output("wbs-upload-xlsx-filename-alert", "children"),
        Output("wbs-upload-xlsx-filename-alert", "color"),
        Output("wbs-upload-xlsx-override-table", "disabled"),
        Output("wbs-toast-via-upload-div", "children"),
        Output("wbs-upload-success-modal", "is_open"),
        Output("wbs-upload-success-modal-body", "children"),
    ],
    [
        Input("wbs-upload-xlsx-launch-modal-button", "n_clicks"),  # user-only
        Input("wbs-upload-xlsx", "contents"),  # user-only
        Input("wbs-upload-xlsx-cancel", "n_clicks"),  # user-only
        Input("wbs-upload-xlsx-override-table", "n_clicks"),  # user-only
    ],
    [State("wbs-current-l1", "value"), State("wbs-upload-xlsx", "filename")],
    prevent_initial_call=True,
)
def handle_xlsx(  # pylint: disable=R0911
    # input(s)
    _: int,
    contents: str,
    __: int,
    ___: int,
    # state(s)
    wbs_l1: str,
    filename: str,
) -> Tuple[bool, str, str, bool, dbc.Toast, bool, List[dcc.Markdown]]:
    """Manage uploading a new xlsx document as the new live table."""
    logging.warning(f"'{du.triggered_id()}' -> handle_xlsx()")

    if not current_user.is_authenticated or not current_user.is_admin:
        logging.error("Cannot handle xlsx since user is not admin.")
        return False, "", "", True, None, False, []

    if du.triggered_id() == "wbs-upload-xlsx-launch-modal-button":
        return True, "", "", True, None, False, []

    if du.triggered_id() == "wbs-upload-xlsx-cancel":
        return False, "", "", True, None, False, []

    if du.triggered_id() == "wbs-upload-xlsx":
        if not filename.endswith(".xlsx"):
            return (
                True,
                f'"{filename}" is not an .xlsx file',
                du.Color.DANGER,
                True,
                None,
                False,
                [],
            )
        return True, f'Uploaded "{filename}"', du.Color.SUCCESS, False, None, False, []

    if du.triggered_id() == "wbs-upload-xlsx-override-table":
        base64_file = contents.split(",")[1]
        try:
            n_records, prev_snap, curr_snap = src.override_table(
                wbs_l1, base64_file, filename
            )
            msg = _get_upload_success_modal_body(
                filename, n_records, prev_snap, curr_snap
            )
            return False, "", "", True, None, True, msg
        except DataSourceException as e:
            error_message = f'Error overriding "{filename}" ({e})'
            return True, error_message, du.Color.DANGER, True, None, False, []

    raise Exception(f"Unaccounted for trigger {du.triggered_id()}")


@app.callback(  # type: ignore[misc]
    [Output("wbs-summary-table", "data"), Output("wbs-summary-table", "columns")],
    [Input("wbs-summary-table-recalculate", "n_clicks")],  # user-only
    [
        State("wbs-current-l1", "value"),
        State("wbs-table-config-cache", "data"),
        State("wbs-current-snapshot-ts", "value"),
    ],
    prevent_initial_call=True,
)
def summarize(
    # input(s)
    _: int,
    # state(s)
    wbs_l1: str,
    state_tconfig_cache: tc.TableConfigParser.CacheType,
    state_snap_current_ts: types.DashVal,
) -> Tuple[types.Table, List[Dict[str, str]]]:
    """Manage uploading a new xlsx document as the new live table."""
    logging.warning(f"'{du.triggered_id()}' -> summarize()")

    try:
        data_table = src.pull_data_table(wbs_l1)
    except DataSourceException:
        return [], []

    tconfig = tc.TableConfigParser(state_tconfig_cache)

    columns = [
        {"id": c, "name": c}
        for c in [
            "Institution",
            "Institutional Lead",
            "Ph.D. Authors",
            "Faculty",
            "Scientists / Post Docs",
            "Ph.D. Students",
            "WBS 2.1 Program Management",
            "WBS 2.2 Detector Operations & Maintenance",
            "WBS 2.3 Computing & Data Management",
            "WBS 2.4 Data Processing & Simulation",
            "WBS 2.5 Software",
            "WBS 2.6 Calibration",
            "Total",
        ]
    ]

    def _sum_it(_inst: str, _l2: str = "") -> float:
        return sum(
            float(r["FTE"])
            for r in data_table
            if r
            and r["FTE"]  # skip blanks (also 0s)
            and r["Institution"] == _inst
            and (not _l2 or r["WBS L2"] == _l2)
        )

    summary_table: types.Table = []
    for inst_full, abbrev in tconfig.get_institutions_w_abbrevs(wbs_l1):
        phds, faculty, sci, grad, __ = src.pull_institution_values(
            wbs_l1, state_snap_current_ts, abbrev
        )
        # TODO -- get rid of hard-coding
        summary_table.append(
            {
                "Institution": inst_full,
                "Ph.D. Authors": phds if phds else 0,
                "Faculty": faculty if faculty else 0,
                "Scientists / Post Docs": sci if sci else 0,
                "Ph.D. Students": grad if grad else 0,
                "WBS 2.1 Program Management": _sum_it(
                    abbrev, "2.1 Program Coordination"
                ),
                "WBS 2.2 Detector Operations & Maintenance": _sum_it(
                    abbrev, "2.2 Detector Operations & Maintenance (Online)"
                ),
                "WBS 2.3 Computing & Data Management": _sum_it(
                    abbrev, "2.3 Computing & Data Management Services"
                ),
                "WBS 2.4 Data Processing & Simulation": _sum_it(
                    abbrev, "2.4 Data Processing & Simulation Services"
                ),
                "WBS 2.5 Software": _sum_it(abbrev, "2.5 Software"),
                "WBS 2.6 Calibration": _sum_it(abbrev, "2.6 Calibration"),
                "Total": _sum_it(abbrev),
            }
        )

    return summary_table, columns
