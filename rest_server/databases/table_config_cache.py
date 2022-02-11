"""Interface for retrieving values for the table config."""


import asyncio
import time
from dataclasses import dataclass
from distutils.util import strtobool
from typing import Any, Dict, Final, List, Tuple, TypedDict, Union

from krs import institutions as krs_institutions  # type: ignore[import]
from krs import token

from .. import wbs
from . import columns

US = "US"
NON_US = "Non-US"


class _ColumnConfigTypedDict(TypedDict, total=False):
    """TypedDict for column configs."""

    width: int
    tooltip: str
    non_editable: bool
    hidden: bool
    options: List[str]
    sort_value: int
    conditional_parent: str
    conditional_options: Dict[str, List[str]]
    border_left: bool
    on_the_fly: bool
    funding_source: bool
    numeric: bool


_LABOR_CATEGORY_DICTIONARY: Dict[str, str] = {
    # Science
    "KE": "Key Personnel (Faculty Members)",
    "SC": "Scientist",
    "PO": "Postdoctoral Associates",
    "GR": "Graduate Students (PhD Students)",
    # Technical
    "AD": "Administration",
    "CS": "Computer Science",
    "DS": "Data Science",
    "EN": "Engineering",
    "IT": "Information Technology",
    "MA": "Manager",
    "WO": "Winterover",
}

MAX_CACHE_AGE = 60 * 60  # seconds


@dataclass(frozen=True)
class Institution:
    """Hold minimal institution data."""

    short_name: str
    long_name: str
    is_us: bool
    has_mou: bool


def convert_krs_institutions(response: Dict[str, Any]) -> List[Institution]:
    """Convert from krs response data to List[Institution]."""
    insts: List[Institution] = []
    for inst, attrs in response.items():
        insts.append(
            Institution(
                short_name=inst,
                long_name=attrs["name"],
                is_us=bool(strtobool(attrs["is_US"])),
                has_mou=bool(strtobool(attrs["has_mou"])),
            )
        )
    return insts


def request_krs_institutions() -> List[Institution]:
    """Grab the master list of institutions along with their details."""
    rc = token.get_rest_client()

    response = asyncio.get_event_loop().run_until_complete(
        krs_institutions.list_insts_flat(
            filter_func=lambda _, attrs: attrs.get("has_mou", "") == "true",
            rest_client=rc,
        )
    )

    return convert_krs_institutions(response)


class TableConfigCache:
    """Manage the collection and parsing of the table config."""

    def __init__(self) -> None:
        self.column_configs, self.institutions = self._build()
        self._timestamp = int(time.time())

    def refresh(self) -> None:
        """Get/Create the most recent table-config doc."""
        if int(time.time()) - self._timestamp < MAX_CACHE_AGE:
            return
        self.column_configs, self.institutions = self._build()
        self._timestamp = int(time.time())

    @staticmethod
    def _build() -> Tuple[Dict[str, _ColumnConfigTypedDict], List[Institution]]:
        """Build the table config."""
        tooltip_funding_source_value: Final[str] = (
            "This number is dependent on the Funding Source and FTE. "
            "Changing those values will affect this number."
        )

        institutions = request_krs_institutions()

        # build column-configs
        column_configs: Final[Dict[str, _ColumnConfigTypedDict]] = {
            columns.WBS_L2: {
                "width": 115,
                "sort_value": 70,
                "tooltip": "WBS Level 2 Category",
            },
            columns.WBS_L3: {
                "width": 115,
                "sort_value": 60,
                "tooltip": "WBS Level 3 Category",
            },
            columns.US_NON_US: {
                "width": 50,
                "non_editable": True,
                "hidden": True,
                "border_left": True,
                "on_the_fly": True,
                "sort_value": 50,
                "tooltip": "The institution's region. This cannot be changed.",
            },
            columns.INSTITUTION: {
                "width": 70,
                "options": sorted(set(inst.short_name for inst in institutions)),
                "border_left": True,
                "sort_value": 40,
                "tooltip": "The institution. This cannot be changed.",
            },
            columns.LABOR_CAT: {
                "width": 50,
                "options": sorted(_LABOR_CATEGORY_DICTIONARY.keys()),
                "sort_value": 30,
                "tooltip": "The labor category",
            },
            columns.NAME: {
                "width": 100,
                "sort_value": 20,
                "tooltip": "LastName, FirstName",
            },
            columns.TASK_DESCRIPTION: {
                "width": 300,
                "tooltip": "A description of the task",
            },
            columns.SOURCE_OF_FUNDS_US_ONLY: {
                "width": 100,
                "conditional_parent": columns.US_NON_US,
                "conditional_options": {
                    US: [
                        columns.NSF_MO_CORE,
                        columns.NSF_BASE_GRANTS,
                        columns.US_IN_KIND,
                    ],
                    NON_US: [columns.NON_US_IN_KIND],
                },
                "border_left": True,
                "sort_value": 10,
                "tooltip": "The funding source",
            },
            columns.FTE: {
                "width": 50,
                "numeric": True,
                "tooltip": "FTE for funding source",
            },
            columns.TOTAL_COL: {
                "width": 100,
                "non_editable": True,
                "hidden": True,
                "border_left": True,
                "on_the_fly": True,
                "tooltip": "TOTAL-ROWS ONLY: FTE totals to the right refer to this category.",
            },
            columns.NSF_MO_CORE: {
                "width": 50,
                "funding_source": True,
                "non_editable": True,
                "hidden": True,
                "numeric": True,
                "on_the_fly": True,
                "tooltip": tooltip_funding_source_value,
            },
            columns.NSF_BASE_GRANTS: {
                "width": 50,
                "funding_source": True,
                "non_editable": True,
                "hidden": True,
                "numeric": True,
                "on_the_fly": True,
                "tooltip": tooltip_funding_source_value,
            },
            columns.US_IN_KIND: {
                "width": 50,
                "funding_source": True,
                "non_editable": True,
                "hidden": True,
                "numeric": True,
                "on_the_fly": True,
                "tooltip": tooltip_funding_source_value,
            },
            columns.NON_US_IN_KIND: {
                "width": 50,
                "funding_source": True,
                "non_editable": True,
                "hidden": True,
                "numeric": True,
                "on_the_fly": True,
                "tooltip": tooltip_funding_source_value,
            },
            columns.GRAND_TOTAL: {
                "width": 50,
                "numeric": True,
                "non_editable": True,
                "hidden": True,
                "border_left": True,
                "on_the_fly": True,
                "tooltip": "This is is the total of the four FTEs to the left.",
            },
            columns.ID: {
                "width": 0,
                "non_editable": True,
                "border_left": True,
                "hidden": True,
            },
            columns.TIMESTAMP: {
                "width": 100,
                "non_editable": True,
                "border_left": True,
                "hidden": True,
                "tooltip": f"{columns.TIMESTAMP} (you may need to refresh to reflect a recent update)",
            },
            columns.EDITOR: {
                "width": 100,
                "non_editable": True,
                "hidden": True,
                "tooltip": f"{columns.EDITOR} (you may need to refresh to reflect a recent update)",
            },
        }

        return column_configs, institutions

    def us_or_non_us(self, inst_name: str) -> str:
        """Return "US" or "Non-US" per institution name."""
        for inst in self.institutions:
            if inst.short_name == inst_name:
                if inst.is_us:
                    return US
                return NON_US
        return ""

    def get_columns(self) -> List[str]:
        """Get the columns."""
        return list(self.column_configs.keys())

    def get_institution_long_and_short(self) -> List[Tuple[str, str]]:
        """Get the institutions' long-names and (regular/short) names."""
        return [(inst.long_name, inst.short_name) for inst in self.institutions]

    def get_labor_categories_and_abbrevs(
        self,
    ) -> List[Tuple[str, str]]:  # pylint:disable=no-self-use
        """Get the labor categories and their abbreviations."""
        return [(name, abbrev) for abbrev, name in _LABOR_CATEGORY_DICTIONARY.items()]

    @staticmethod
    def get_l2_categories(l1: str) -> List[str]:
        """Get the L2 categories."""
        return list(wbs.WORK_BREAKDOWN_STRUCTURES[l1].keys())

    @staticmethod
    def get_l3_categories_by_l2(l1: str, l2: str) -> List[str]:
        """Get the L3 categories for an L2 value."""
        return wbs.WORK_BREAKDOWN_STRUCTURES[l1][l2]

    def get_simple_dropdown_menus(self, l1: str) -> Dict[str, List[str]]:
        """Get the columns that are simple dropdowns, with their options."""
        ret = {
            col: config["options"]
            for col, config in self.column_configs.items()
            if "options" in config
        }
        ret[columns.WBS_L2] = self.get_l2_categories(l1)
        return ret

    def get_conditional_dropdown_menus(
        self, l1: str
    ) -> Dict[str, Tuple[str, Dict[str, List[str]]]]:
        """Get the columns (and conditions) that are conditionally dropdowns.

        Example:
        {'Col-Name-A' : ('Parent-Col-Name-1', {'Parent-Val-I' : ['Option-Alpha', ...] } ) }
        """
        ret = {
            col: (config["conditional_parent"], config["conditional_options"])
            for col, config in self.column_configs.items()
            if ("conditional_parent" in config) and ("conditional_options" in config)
        }
        ret[columns.WBS_L3] = (columns.WBS_L2, wbs.WORK_BREAKDOWN_STRUCTURES[l1])
        return ret

    def get_dropdowns(self, l1: str) -> List[str]:
        """Get the columns that are dropdowns."""
        return list(self.get_simple_dropdown_menus(l1).keys()) + list(
            self.get_conditional_dropdown_menus(l1).keys()
        )

    def get_numerics(self) -> List[str]:
        """Get the columns that have numeric data."""
        return [
            col for col, config in self.column_configs.items() if config.get("numeric")
        ]

    def get_non_editables(self) -> List[str]:
        """Get the columns that are not editable."""
        return [
            col
            for col, config in self.column_configs.items()
            if config.get("non_editable")
        ]

    def get_hiddens(self) -> List[str]:
        """Get the columns that are hidden."""
        return [
            col for col, config in self.column_configs.items() if config.get("hidden")
        ]

    def get_widths(self) -> Dict[str, int]:
        """Get the widths of each column."""
        return {col: config["width"] for col, config in self.column_configs.items()}

    def get_tooltips(self) -> Dict[str, str]:
        """Get the widths of each column."""
        return {
            col: config["tooltip"]
            for col, config in self.column_configs.items()
            if config.get("tooltip")
        }

    def get_border_left_columns(self) -> List[str]:
        """Get the columns that have a left border."""
        return [
            col
            for col, config in self.column_configs.items()
            if config.get("border_left")
        ]

    def get_page_size(self) -> int:  # pylint: disable=no-self-use
        """Get page size."""
        return 19

    def get_on_the_fly_fields(self) -> List[str]:
        """Get names of fields created on-the-fly, data not stored."""
        return [
            col
            for col, config in self.column_configs.items()
            if config.get("on_the_fly")
        ]

    def sort_key(self, k: Dict[str, Union[int, float, str]]) -> Tuple[Any, ...]:
        """Sort key for the table."""
        sort_keys: List[Union[int, float, str]] = []

        column_orders = {
            col: config["sort_value"]
            for col, config in self.column_configs.items()
            if "sort_value" in config
        }
        columns_by_precedence = sorted(
            column_orders.keys(), key=lambda x: column_orders[x], reverse=True
        )

        for col in columns_by_precedence:
            sort_keys.append(k.get(col, "ZZZZ"))  # HACK: sort empty/missing values last

        return tuple(sort_keys)