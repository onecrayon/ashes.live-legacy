from typing import Dict, List, Tuple, Optional

from app.models.release import Release


def get_release_mapping(release_mapping: Optional[Dict[int, Release]] = None) -> Dict[int, Release]:
    """Returns a dictionary with the release ID mapped to the release object"""
    if release_mapping:
        return release_mapping
    releases = Release.query.all()
    return {x.id: x for x in releases}


def get_release_list() -> List[Tuple[int, str]]:
    """Returns a list of tuples like (id, name) for all releases"""
    releases = Release.query.all()
    return [{
        'id': x.id,
        'name': x.name,
        'is_phg': x.is_phg,
        'is_promo': x.is_promo,
    } for x in releases]
