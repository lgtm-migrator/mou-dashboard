"""Unit test web_app module."""


# pylint: disable=W0212,W0621


import inspect
import itertools
import sys
from copy import deepcopy
from enum import Enum
from typing import Any, Final, Iterator, List, TypedDict
from unittest.mock import patch

import pytest
import requests

sys.path.append(".")
import web_app.utils  # isort:skip  # noqa # pylint: disable=E0401,C0413
from web_app.data_source import (  # isort:skip  # noqa # pylint: disable=E0401,C0413
    data_source as src,
    table_config as tc,
    connections,
)

WBS = "mo"


@pytest.fixture(autouse=True)
def clear_all_cachetools_func_caches() -> Iterator[None]:
    """Clear all `cachetools.func` caches, everywhere."""
    yield
    connections._cached_get_institutions_infos.cache_clear()  # type: ignore[attr-defined]
    tc.TableConfigParser._cached_get_configs.cache_clear()  # type: ignore[attr-defined]
    web_app.data_source.connections.CurrentUser._cached_get_info.cache_clear()  # type: ignore[attr-defined]


@pytest.fixture
def tconfig() -> Iterator[tc.TableConfigParser]:
    """Provide a TableConfigParser instance."""
    tconfig_cache: tc.TableConfigParser.CacheType = {
        WBS: {  # type: ignore[typeddict-item]
            "simple_dropdown_menus": {"Alpha": ["A1", "A2"], "Beta": []},
            "conditional_dropdown_menus": {
                "Dish": (
                    "Alpha",
                    {
                        "A1": ["chicken", "beef", "pork", "fish", "shrimp", "goat"],
                        "A2": [],
                    },
                ),
            },
            "columns": ["Alpha", "Dish", "F1", "Beta"],
        }
    }
    with patch(
        "web_app.data_source.table_config.TableConfigParser._cached_get_configs"
    ) as mock_cgc:
        mock_cgc.return_value = tconfig_cache
        yield tc.TableConfigParser(WBS)


class TestPrivateDataSource:
    """Test private functions in dash_source.py."""

    RECORD: Final[web_app.utils.types.Record] = {"a": "AA", "b": "BB", "c": "CC"}

    def _get_new_record(self) -> web_app.utils.types.Record:
        return deepcopy(self.RECORD)

    def test_add_original_copies_to_record(self, tconfig: tc.TableConfigParser) -> None:
        """Test add_original_copies_to_record()."""
        record = self._get_new_record()
        record_orig = deepcopy(record)

        for _ in range(2):
            record_out = src._convert_record_rest_to_dash(record, tconfig)
            assert record_out == record  # check in-place update
            assert len(record) == (2 * len(record_orig)) + 2  # editor + editor_original
            assert tconfig.const.EDITOR in record
            # check copied values
            for key in record_orig.keys():
                assert record_orig[key] == record[key]
                assert record_orig[key] == record[src.get_touchstone_name(key)]

    def test_add_original_copies_to_record_novel(
        self, tconfig: tc.TableConfigParser
    ) -> None:
        """Test add_original_copies_to_record(novel=True)."""
        record = self._get_new_record()
        record_orig = deepcopy(record)

        for _ in range(2):
            record_out = src._convert_record_rest_to_dash(record, tconfig, novel=True)
            assert record_out == record  # check in-place update
            assert len(record) == (2 * len(record_orig)) + 2  # editor + editor_original
            assert tconfig.const.EDITOR in record
            # check copied values
            for key in record_orig.keys():
                assert record_orig[key] == record[key]
                # check only keys were copied with touchstone columns, not values
                assert record_orig[key] != record[src.get_touchstone_name(key)]
                assert record[src.get_touchstone_name(key)] == ""

    def test_without_original_copies_from_record(
        self, tconfig: tc.TableConfigParser
    ) -> None:
        """Test without_original_copies_from_record()."""
        record = self._get_new_record()
        record_orig = deepcopy(record)

        src._convert_record_rest_to_dash(record, tconfig)
        record_out = src._convert_record_dash_to_rest(record)

        assert record_out != record
        assert record_out.pop(tconfig.const.EDITOR) == "—"
        assert record_out == record_orig

    @staticmethod
    def test_remove_invalid_data(tconfig: tc.TableConfigParser) -> None:
        """Test _remove_invalid_data() & _convert_record_dash_to_rest()."""
        # pylint: disable=R0915,R0912

        def _assert(
            _orig: web_app.utils.types.Record, _good: web_app.utils.types.Record
        ) -> None:
            assert (
                _good
                == src._remove_invalid_data(_orig, tconfig)
                == src._convert_record_dash_to_rest(_orig, tconfig)
            )

        class Scenario(Enum):  # pylint: disable=C0115
            MISSING, GOOD, BAD, BLANK = 1, 2, 3, 4

        # Test every combination of a simple-dropdown-type & a conditional-dropdown type
        for alpha, dish in itertools.product(list(Scenario), list(Scenario)):
            record: web_app.utils.types.Record = {"F1": 0}

            if alpha != Scenario.MISSING:
                record["Alpha"] = {
                    Scenario.GOOD: "A1",
                    Scenario.BAD: "whatever",
                    Scenario.BLANK: "",
                }[alpha]

            if dish != Scenario.MISSING:
                record["Dish"] = {
                    Scenario.GOOD: "pork",
                    Scenario.BAD: "this",
                    Scenario.BLANK: "",
                }[dish]

            # Test all 16 combinations
            out = deepcopy(record)
            out["Beta"] = ""
            if (alpha, dish) == (Scenario.MISSING, Scenario.MISSING):
                out["Alpha"] = ""
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.MISSING, Scenario.GOOD):
                out["Alpha"] = ""
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.MISSING, Scenario.BAD):
                out["Alpha"] = ""
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.MISSING, Scenario.BLANK):
                out["Alpha"] = ""
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.GOOD, Scenario.MISSING):
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.GOOD, Scenario.GOOD):
                _assert(record, out)
            elif (alpha, dish) == (Scenario.GOOD, Scenario.BAD):
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.GOOD, Scenario.BLANK):
                _assert(record, out)
            elif (alpha, dish) == (Scenario.BAD, Scenario.MISSING):
                out["Dish"] = ""
                out["Alpha"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.BAD, Scenario.GOOD):
                out["Alpha"] = ""
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.BAD, Scenario.BAD):
                out["Dish"] = ""
                out["Alpha"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.BAD, Scenario.BLANK):
                out["Alpha"] = ""
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.BLANK, Scenario.MISSING):
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.BLANK, Scenario.GOOD):
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.BLANK, Scenario.BAD):
                out["Dish"] = ""
                _assert(record, out)
            elif (alpha, dish) == (Scenario.BLANK, Scenario.BLANK):
                _assert(record, out)
            else:
                raise Exception(record)


class TestDataSource:
    """Test data_source.py."""

    @staticmethod
    @pytest.fixture
    def mock_rest(mocker: Any) -> Any:
        """Patch mock_rest."""
        return mocker.patch("web_app.data_source.connections._rest_connection")

    @staticmethod
    def test_pull_data_table(mock_rest: Any, tconfig: tc.TableConfigParser) -> None:
        """Test pull_data_table()."""
        response = {"foo": 0, "table": [{"a": "a"}, {"b": 2}, {"c": None}]}
        bodies = [
            {  # Default values
                "institution": "",
                "labor": "",
                "total_rows": False,
                "snapshot": "",
                "restore_id": "",
            },
            {  # Other values
                "institution": "bar",
                "labor": "baz",
                "total_rows": True,
                "snapshot": "123",
                "restore_id": "456789456123",
            },
        ]

        for i, _ in enumerate(bodies):
            # Call
            mock_rest.return_value.request_seq.return_value = response
            # Default values
            if i == 0:
                ret = src.pull_data_table(WBS, tconfig)
            # Other values
            else:
                ret = src.pull_data_table(
                    WBS,
                    tconfig,
                    institution=bodies[i]["institution"],  # type: ignore[arg-type]
                    labor=bodies[i]["labor"],  # type: ignore[arg-type]
                    with_totals=bodies[i]["total_rows"],  # type: ignore[arg-type]
                    snapshot_ts=bodies[i]["snapshot"],  # type: ignore[arg-type]
                    restore_id=bodies[i]["restore_id"],  # type: ignore[arg-type]
                )

            # Assert
            mock_rest.return_value.request_seq.assert_called_with(
                "GET", f"/table/data/{WBS}", bodies[i]
            )
            assert ret == response["table"]

    @staticmethod
    @patch("web_app.data_source.connections.CurrentUser._get_info")
    def test_push_record(
        current_user: Any, mock_rest: Any, tconfig: tc.TableConfigParser
    ) -> None:
        """Test push_record()."""
        current_user.return_value = web_app.data_source.connections.UserInfo(
            "t.hanks", ["/institutions/IceCube/UW-Madison/_admin"], "foobarbaz"
        )
        unrealistic_hardcoded_resp = {
            "foo": 0,
            "record": {"x": "foo", "y": 22, "z": "z"},
            # "editor": "t.hanks",
        }

        class _Body(TypedDict, total=False):
            record: web_app.utils.types.Record
            institution: str
            labor: str
            editor: str

        bodies: List[_Body] = [
            # Default values
            {"record": {"BAR": 23}, "editor": "t.hanks"},
            # Other values
            {
                "institution": "foo",
                "labor": "bar",
                "record": {"a": 1},
                "editor": "t.hanks",
            },
        ]

        for i, _ in enumerate(bodies):
            # Call
            mock_rest.return_value.request_seq.return_value = unrealistic_hardcoded_resp
            # Default values
            if i == 0:
                ret = src.push_record(WBS, bodies[0]["record"], tconfig)
            # Other values
            else:
                ret = src.push_record(
                    WBS,
                    bodies[i]["record"],
                    tconfig,
                    labor=bodies[i]["labor"],
                    institution=bodies[i]["institution"],
                )

            # Assert
            posted = deepcopy(bodies[i])
            # fields not included in `push_record()` are added as blanks
            posted["record"].update({"Alpha": "", "Dish": "", "F1": "", "Beta": ""})
            mock_rest.return_value.request_seq.assert_called_with(
                "POST", f"/record/{WBS}", posted
            )
            assert ret == unrealistic_hardcoded_resp["record"]

    @staticmethod
    @patch("web_app.data_source.connections.CurrentUser._get_info")
    def test_delete_record(current_user: Any, mock_rest: Any) -> None:
        """Test delete_record()."""
        current_user.return_value = web_app.data_source.connections.UserInfo(
            "t.hanks", ["/institutions/IceCube/UW-Madison/_admin"], "foobarbaz"
        )
        record_id = "23"

        # Call
        src.delete_record(WBS, record_id)  # raises if fail

        # Assert
        mock_rest.return_value.request_seq.assert_called_with(
            "DELETE", f"/record/{WBS}", {"record_id": record_id, "editor": "t.hanks"}
        )

        # Fail Test #
        # Call
        mock_rest.return_value.request_seq.side_effect = requests.exceptions.HTTPError

        with pytest.raises(connections.DataSourceException):
            src.delete_record(WBS, record_id)

        # Assert
        mock_rest.return_value.request_seq.assert_called_with(
            "DELETE", f"/record/{WBS}", {"record_id": record_id, "editor": "t.hanks"}
        )

    @staticmethod
    @patch("web_app.data_source.connections.CurrentUser.is_loggedin")
    @patch("web_app.data_source.connections.CurrentUser._get_info")
    def test_list_snapshot_timestamps(
        current_user: Any, mock_ili: Any, mock_rest: Any
    ) -> None:
        """Test list_snapshot_timestamps()."""
        current_user.return_value = web_app.data_source.connections.UserInfo(
            "t.hanks", ["/tokens/mou-dashboard-admin"], "foobarbaz"
        )
        mock_ili.return_value = True
        response = {
            "snapshots": [
                {"timestamp": "a", "name": "aye", "creator": "George"},
                {"timestamp": "b", "name": "bee", "creator": "Ringo"},
                {"timestamp": "c", "name": "see", "creator": "John"},
                {"timestamp": "d", "name": "dee", "creator": "Paul"},
            ],
        }

        # Call
        mock_rest.return_value.request_seq.return_value = response
        ret = src.list_snapshots(WBS)

        # Assert
        mock_rest.return_value.request_seq.assert_called_with(
            "GET", f"/snapshots/list/{WBS}", {"is_admin": True}
        )
        assert sorted(ret, key=lambda k: k["timestamp"]) == response["snapshots"]

    @staticmethod
    @patch("web_app.data_source.connections.CurrentUser._get_info")
    def test_create_snapshot(current_user: Any, mock_rest: Any) -> None:
        """Test create_snapshot()."""
        current_user.return_value = web_app.data_source.connections.UserInfo(
            "t.hanks", ["/institutions/IceCube/UW-Madison/_admin"], "foobarbaz"
        )
        response = {"timestamp": "a", "foo": "bar"}

        # Call
        mock_rest.return_value.request_seq.return_value = response
        ret = src.create_snapshot(WBS, "snap_name")

        # Assert
        mock_rest.return_value.request_seq.assert_called_with(
            "POST",
            f"/snapshots/make/{WBS}",
            {"creator": "t.hanks", "name": "snap_name"},
        )
        assert ret == response


class TestTableConfig:
    """Test table_config.py."""

    @staticmethod
    @pytest.fixture
    def mock_rest(mocker: Any) -> Any:
        """Patch mock_rest."""
        return mocker.patch("web_app.data_source.connections._rest_connection")

    @staticmethod
    def test_consts(tconfig: tc.TableConfigParser) -> None:
        """Check the conts, these correspond to the column names."""
        assert tconfig.const.ID == "_id"
        assert tconfig.const.WBS_L2 == "WBS L2"
        assert tconfig.const.WBS_L3 == "WBS L3"
        assert tconfig.const.LABOR_CAT == "Labor Cat."
        assert tconfig.const.US_NON_US == "US / Non-US"
        assert tconfig.const.INSTITUTION == "Institution"
        assert tconfig.const.NAME == "Name"
        assert tconfig.const.TASK_DESCRIPTION == "Task Description"
        assert tconfig.const.SOURCE_OF_FUNDS_US_ONLY == "Source of Funds (U.S. Only)"
        assert tconfig.const.FTE == "FTE"
        assert tconfig.const.NSF_MO_CORE == "NSF M&O Core"
        assert tconfig.const.NSF_BASE_GRANTS == "NSF Base Grants"
        assert tconfig.const.US_IN_KIND == "US In-Kind"
        assert tconfig.const.NON_US_IN_KIND == "Non-US In-Kind"
        assert tconfig.const.GRAND_TOTAL == "Grand Total"
        assert tconfig.const.TOTAL_COL == "Total-Row Description"
        assert tconfig.const.TIMESTAMP == "Date & Time of Last Edit"
        assert tconfig.const.EDITOR == "Name of Last Editor"

    @staticmethod
    def test_table_config(mock_rest: Any) -> None:
        """Test TableConfig()."""
        # pylint: disable=R0915,R0912

        # nonsense data, but correctly typed
        resp: tc.TableConfigParser.CacheType = {
            WBS: {
                "columns": ["a", "b", "c", "d"],
                "simple_dropdown_menus": {
                    "a": ["1", "2", "3"],
                    "c": ["4", "44", "444"],
                },
                "labor_categories": sorted([("foobar", "FB"), ("baz", "BZ")]),
                "conditional_dropdown_menus": {
                    "column1": (
                        "parent_of_1",
                        {
                            "optA": ["alpha", "a", "atlantic"],
                            "optB": ["beta", "b", "boat"],
                        },
                    ),
                    "column2": (
                        "parent_of_2",
                        {
                            "optD": ["delta", "d", "dock"],
                            "optG": ["gamma", "g", "gulf"],
                        },
                    ),
                },
                "dropdowns": ["gamma", "mu"],
                "numerics": ["foobarbaz"],
                "non_editables": ["alpha", "beta"],
                "hiddens": ["z", "y", "x"],
                "widths": {"Zetta": 888, "Yotta": -50},
                "border_left_columns": ["ee", "e"],
                "page_size": 55,
                "tooltips": {"ham": "blah"},
            }
        }

        # Call
        mock_rest.return_value.request_seq.return_value = resp
        table_config = tc.TableConfigParser(WBS)

        # Assert
        mock_rest.return_value.request_seq.assert_called_with(
            "GET", "/table/config", None
        )
        assert table_config._configs == resp

        # no-argument methods
        assert table_config.get_table_columns() == resp[WBS]["columns"]
        assert (
            table_config.get_labor_categories_w_abbrevs()
            == resp[WBS]["labor_categories"]
        )
        assert table_config.get_hidden_columns() == resp[WBS]["hiddens"]
        assert table_config.get_dropdown_columns() == resp[WBS]["dropdowns"]
        assert table_config.get_page_size() == resp[WBS]["page_size"]

        # is_column_*()
        for col in resp[WBS]["dropdowns"]:
            assert table_config.is_column_dropdown(col)
            assert not table_config.is_column_dropdown(col + "!")
        for col in resp[WBS]["numerics"]:
            assert table_config.is_column_numeric(col)
            assert not table_config.is_column_numeric(col + "!")
        for col in resp[WBS]["non_editables"]:
            assert not table_config.is_column_editable(col)
            assert table_config.is_column_editable(col + "!")
        for col in resp[WBS]["simple_dropdown_menus"]:
            assert table_config.is_simple_dropdown(col)
            assert not table_config.is_simple_dropdown(col + "!")
        for col in resp[WBS]["conditional_dropdown_menus"]:
            assert table_config.is_conditional_dropdown(col)
            assert not table_config.is_conditional_dropdown(col + "!")
        for col in resp[WBS]["border_left_columns"]:
            assert table_config.has_border_left(col)
            assert not table_config.has_border_left(col + "!")

        # tooltips
        for col, tooltip in resp[WBS]["tooltips"].items():
            assert tooltip == table_config.get_column_tooltip(col)

        # get_simple_column_dropdown_menu()
        for col, menu in resp[WBS]["simple_dropdown_menus"].items():
            assert table_config.get_simple_column_dropdown_menu(col) == menu
            with pytest.raises(KeyError):
                table_config.get_simple_column_dropdown_menu(col + "!")

        # get_conditional_column_parent()
        for col, par_opts in resp[WBS]["conditional_dropdown_menus"].items():
            assert table_config.get_conditional_column_parent_and_options(col) == (
                par_opts[0],  # parent
                list(par_opts[1].keys()),  # options
            )
            with pytest.raises(KeyError):
                table_config.get_conditional_column_parent_and_options(col + "!")

        # get_conditional_column_dropdown_menu()
        for col, par_opts in resp[WBS]["conditional_dropdown_menus"].items():
            for parent_col_option, menu in par_opts[1].items():
                assert (
                    table_config.get_conditional_column_dropdown_menu(
                        col, parent_col_option
                    )
                    == menu
                )
                with pytest.raises(KeyError):
                    table_config.get_conditional_column_dropdown_menu(
                        col + "!", parent_col_option
                    )
                    table_config.get_conditional_column_dropdown_menu(
                        col, parent_col_option + "!"
                    )

        # Error handling methods
        for col, wid in resp[WBS]["widths"].items():
            assert table_config.get_column_width(col) == wid
        # reset
        tc.TableConfigParser._cached_get_configs.cache_clear()  # type: ignore[attr-defined]
        mock_rest.return_value.request_seq.return_value = {}
        # call
        table_config = tc.TableConfigParser(WBS)
        for col, wid in resp[WBS]["widths"].items():
            default = (
                inspect.signature(table_config.get_column_width)
                .parameters["default"]
                .default
            )
            assert table_config.get_column_width(col) == default
