"""Meta information utilities."""


def map_meta_information_name(key: str) -> str:
    """Map meta key."""
    mapping = {"datetime": "date"}
    if key in mapping:
        return mapping[key]
    else:
        return key
