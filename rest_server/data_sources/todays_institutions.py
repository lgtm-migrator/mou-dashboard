"""Tools for getting info on the state of today's institutions."""

from dataclasses import dataclass
from distutils.util import strtobool
import logging
from typing import Any, Dict, List

from krs import institutions as krs_institutions  # type: ignore[import]
from krs import token


@dataclass(frozen=True)
class Institution:
    """Hold minimal institution data."""

    short_name: str
    long_name: str
    is_us: bool
    has_mou: bool
    institution_lead_uid: str


def convert_krs_institutions(response: Dict[str, Any]) -> List[Institution]:
    """Convert from krs response data to List[Institution]."""
    insts: List[Institution] = []
    for inst, attrs in response.items():
        if not attrs:
            continue
        try:
            has_mou = bool(strtobool(attrs.get("has_mou", "false")))
            if has_mou and 'name' not in attrs:
                raise KeyError('"name" is required')
            if has_mou and 'is_US' not in attrs:
                raise KeyError('"is_US" is required')
            insts.append(
                Institution(
                    short_name=inst,
                    long_name=attrs.get("name", inst),
                    is_us=bool(strtobool(attrs.get("is_US", "false"))),
                    has_mou=has_mou,
                    institution_lead_uid=attrs.get("institutionLeadUid", ""),
                )
            )
        except Exception:
            logging.warning('bad inst attributes for inst %s', inst, exc_info=True)
            raise
    return insts


def filter_krs_institutions(group_path: str, attrs: Dict[str, Any]) -> bool:
    """Filters for institutions in IceCube or Gen2 experiments"""
    experiment = group_path.split('/')[2]
    if experiment in ('IceCube', 'IceCube-Gen2'):
        return True
    else:
        return False


async def request_krs_institutions() -> List[Institution]:
    """Grab the master list of institutions along with their details."""
    rc = token.get_rest_client()

    response = await krs_institutions.list_insts_flat(
        rest_client=rc,
        filter_func=filter_krs_institutions,
        attr_whitelist=["name", "is_US", "has_mou", "institutionLeadUid"],
    )

    return convert_krs_institutions(response)
