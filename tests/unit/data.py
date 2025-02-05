"""Testing data."""

import pprint
import random
import sys
from typing import Any, Final
from unittest.mock import AsyncMock, Mock, patch

import pytest

from .. import institution_list

sys.path.append(".")
# pylint: disable=E0401,C0413,C0411
from rest_server.utils import types  # isort:skip  # noqa
from rest_server.data_sources import (  # isort:skip  # noqa
    table_config_cache,
    columns,
)


WBS: Final[str] = "mo"


FTE_ROWS: Final[types.Table] = [
    {
        "FTE": 0.49982416070757496,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.0 Program Coordination",
    },
    {
        "FTE": 0.02113568893093143,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.0 Program Coordination",
    },
    {
        "FTE": 0.11154963161843479,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.0 Program Coordination",
    },
    {
        "FTE": 0.9192678481343621,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.0 Program Coordination",
    },
    {
        "FTE": 0.37123355031139427,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.0 Program Coordination",
    },
    {
        "FTE": 0.04446193894639161,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.0 Program Coordination",
    },
    {
        "FTE": 0.8790863080227265,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.0 Program Coordination",
    },
    {
        "FTE": 0.7663959318864819,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.0 Program Coordination",
    },
    {
        "FTE": 0.520136097464622,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.1 Administration",
    },
    {
        "FTE": 0.5803656907062612,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.1 Administration",
    },
    {
        "FTE": 0.3752971081334566,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.1 Administration",
    },
    {
        "FTE": 0.4873251796122231,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.1 Administration",
    },
    {
        "FTE": 0.9807711433936455,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.1 Administration",
    },
    {
        "FTE": 0.8987838119272779,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.1 Administration",
    },
    {
        "FTE": 0.04358317179986515,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.1 Administration",
    },
    {
        "FTE": 0.8808657685732356,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.1 Administration",
    },
    {
        "FTE": 0.773959808272325,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.2 Engineering and R&D Support",
    },
    {
        "FTE": 0.9245699303387455,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.2 Engineering and R&D Support",
    },
    {
        "FTE": 0.26210644955159024,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.2 Engineering and R&D Support",
    },
    {
        "FTE": 0.33493175909465245,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.2 Engineering and R&D Support",
    },
    {
        "FTE": 0.3776254018537659,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.2 Engineering and R&D Support",
    },
    {
        "FTE": 0.4236181074983122,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.2 Engineering and R&D Support",
    },
    {
        "FTE": 0.037168951681068485,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.2 Engineering and R&D Support",
    },
    {
        "FTE": 0.169199506831905,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.1 Program Coordination",
        "WBS L3": "2.1.2 Engineering and R&D Support",
    },
    {
        "FTE": 0.19437685761542622,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.0 Detector Operations & Maintenance",
    },
    {
        "FTE": 0.2406523379800134,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.0 Detector Operations & Maintenance",
    },
    {
        "FTE": 0.1011477080893406,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.0 Detector Operations & Maintenance",
    },
    {
        "FTE": 0.0733238607965615,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.0 Detector Operations & Maintenance",
    },
    {
        "FTE": 0.46635158504286334,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.0 Detector Operations & Maintenance",
    },
    {
        "FTE": 0.5161233490332815,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.0 Detector Operations & Maintenance",
    },
    {
        "FTE": 0.49885840535629944,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.0 Detector Operations & Maintenance",
    },
    {
        "FTE": 0.4274893700165163,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.0 Detector Operations & Maintenance",
    },
    {
        "FTE": 0.4195683454187139,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.1 Run Coordination",
    },
    {
        "FTE": 0.658919428439551,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.1 Run Coordination",
    },
    {
        "FTE": 0.18662880286853833,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.1 Run Coordination",
    },
    {
        "FTE": 0.6932877725821052,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.1 Run Coordination",
    },
    {
        "FTE": 0.3100524964799366,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.1 Run Coordination",
    },
    {
        "FTE": 0.7085819511378794,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.1 Run Coordination",
    },
    {
        "FTE": 0.7235113039130185,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.1 Run Coordination",
    },
    {
        "FTE": 0.23914219675549853,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.1 Run Coordination",
    },
    {
        "FTE": 0.05310526922200198,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.2 Data Acquisition",
    },
    {
        "FTE": 0.2364149398070674,
        "Source of Funds (U.S. Only)": "Non-US In-Kind",
        "US / Non-US": "Non-US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.2 Data Acquisition",
    },
    {
        "FTE": 0.9269734567691197,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.2 Data Acquisition",
    },
    {
        "FTE": 0.8307364137821496,
        "Source of Funds (U.S. Only)": "NSF Base Grants",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.2 Data Acquisition",
    },
    {
        "FTE": 0.4267522288772331,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.2 Data Acquisition",
    },
    {
        "FTE": 0.19393048415222336,
        "Source of Funds (U.S. Only)": "NSF M&O Core",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.2 Data Acquisition",
    },
    {
        "FTE": 0.9995555944143646,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.2 Data Acquisition",
    },
    {
        "FTE": 0.4674268415008417,
        "Source of Funds (U.S. Only)": "US In-Kind",
        "US / Non-US": "US",
        "WBS L2": "2.2 Detector Operations & Maintenance (Online)",
        "WBS L3": "2.2.2 Data Acquisition",
    },
]


#
# --------------------------------------------------------------------------------------
#


@pytest.mark.asyncio
@patch(
    "krs.institutions.list_insts_flat",
    side_effect=AsyncMock(return_value=institution_list.INSTITUTIONS),
)
@patch("krs.token.get_rest_client", return_value=Mock())
@patch(
    "rest_server.data_sources.table_config_cache.TableConfigCache.get_most_recent_doc"
)
@patch("rest_server.data_sources.table_config_cache.TableConfigCache._insert_replace")
async def _make_fte_rows(mock_ir: Any, mock_gmrd: Any, _: Any, __: Any) -> None:
    # Setup & Mock
    mock_gmrd.side_effect = AsyncMock(return_value=(None, None))  # "db is empty"
    tc_cache = await table_config_cache.TableConfigCache.create()
    mock_ir.side_effect = AsyncMock(return_value=None)  # no-op the db insert

    rows: types.Table = []
    for l2 in [
        "2.1 Program Coordination",
        "2.2 Detector Operations & Maintenance (Online)",
    ]:
        for l3 in tc_cache.get_l3_categories_by_l2(WBS, l2):
            if ".3" in l3:
                break
            # append 2 US for each funding source
            for _ in range(2):
                for fund in [
                    columns.NSF_MO_CORE,
                    columns.NSF_BASE_GRANTS,
                    columns.US_IN_KIND,
                ]:
                    row = {
                        columns.WBS_L2: l2,
                        columns.WBS_L3: l3,
                        columns.US_NON_US: table_config_cache.US,
                    }
                    row[columns.SOURCE_OF_FUNDS_US_ONLY] = fund
                    row[columns.FTE] = random.random() * 1  # type: ignore[assignment]
                    rows.append(row)  # type: ignore[arg-type]

            # append 2 Non-US
            for _ in range(2):
                row = {columns.WBS_L2: l2, columns.WBS_L3: l3}
                row[columns.US_NON_US] = table_config_cache.NON_US
                row[columns.SOURCE_OF_FUNDS_US_ONLY] = columns.NON_US_IN_KIND
                row[columns.FTE] = random.random() * 1  # type: ignore[assignment]
                rows.append(row)  # type: ignore[arg-type]

    rows.sort(key=tc_cache.sort_key)
    pprint.pprint(rows)
