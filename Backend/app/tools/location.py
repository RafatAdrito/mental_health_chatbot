import httpx
from langchain_core.tools import tool

_OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Bangladesh bounding box: (south, west, north, east)
_BANGLADESH_BBOX = (20.7, 88.0, 26.6, 92.7)

# OSM regex used to identify mental-health specialities/facilities.
# Matched case-insensitively against tag values (and, as a fallback, names).
_MENTAL_HEALTH_REGEX = "psychiatry|psychiatric|psychotherapy|psychotherapist|psycholog|mental"

# Each type maps to one or more Overpass clauses that target ONLY
# mental-health related places (not general hospitals/clinics).
_OSM_CLAUSE_MAP: dict[str, list[str]] = {
    "hospital": [
        f'nwr["amenity"="hospital"]["healthcare:speciality"~"{_MENTAL_HEALTH_REGEX}",i]',
        f'nwr["amenity"="hospital"]["name"~"{_MENTAL_HEALTH_REGEX}",i]',
        f'nwr["healthcare"="hospital"]["healthcare:speciality"~"{_MENTAL_HEALTH_REGEX}",i]',
    ],
    "therapist": [
        'nwr["healthcare"="psychotherapist"]',
        f'nwr["healthcare:speciality"~"{_MENTAL_HEALTH_REGEX}",i]',
        f'nwr["amenity"="doctors"]["healthcare:speciality"~"{_MENTAL_HEALTH_REGEX}",i]',
    ],
    "clinic": [
        f'nwr["amenity"="clinic"]["healthcare:speciality"~"{_MENTAL_HEALTH_REGEX}",i]',
        f'nwr["amenity"="clinic"]["name"~"{_MENTAL_HEALTH_REGEX}",i]',
        f'nwr["healthcare"="clinic"]["healthcare:speciality"~"{_MENTAL_HEALTH_REGEX}",i]',
    ],
}

_MOCK_HOSPITALS = [
    {
        "name": "National Institute of Mental Health (NIMH)",
        "address": "Sher-E-Bangla Nagar, Dhaka-1207",
        "phone": "02-9118193",
        "rating": None,
        "maps_link": "https://www.openstreetmap.org/search?query=NIMH+Dhaka",
    },
    {
        "name": "Pabna Mental Hospital",
        "address": "Pabna, Rajshahi Division",
        "phone": "0731-65014",
        "rating": None,
        "maps_link": "https://www.openstreetmap.org/search?query=Pabna+Mental+Hospital",
    },
    {
        "name": "Dhaka Medical College Hospital",
        "address": "Bakshibazar, Dhaka-1000",
        "phone": "02-55165088",
        "rating": None,
        "maps_link": "https://www.openstreetmap.org/search?query=Dhaka+Medical+College+Hospital",
    },
]

_MOCK_THERAPISTS = [
    {
        "name": "Kaan Pete Roi (কান পেতে রই)",
        "address": "Dhaka, Bangladesh",
        "phone": "01779-554391",
        "rating": None,
        "maps_link": "https://www.openstreetmap.org/search?query=Dhaka+Bangladesh",
    },
    {
        "name": "National Mental Health Helpline",
        "address": "Bangladesh",
        "phone": "16789",
        "rating": None,
        "maps_link": "https://www.openstreetmap.org/search?query=Dhaka+Bangladesh",
    },
]

_MOCK_CLINICS = [
    {
        "name": "Centre for the Rehabilitation of the Paralysed (CRP)",
        "address": "Chapain, Savar, Dhaka",
        "phone": "02-7711981",
        "rating": None,
        "maps_link": "https://www.openstreetmap.org/search?query=CRP+Savar+Dhaka",
    },
    {
        "name": "National Institute of Mental Health (NIMH)",
        "address": "Sher-E-Bangla Nagar, Dhaka-1207",
        "phone": "02-9118193",
        "rating": None,
        "maps_link": "https://www.openstreetmap.org/search?query=NIMH+Dhaka",
    },
]

_MOCK_DATA = {
    "hospital": _MOCK_HOSPITALS,
    "therapist": _MOCK_THERAPISTS,
    "clinic": _MOCK_CLINICS,
}


def _is_in_bangladesh(lat: float, lon: float) -> bool:
    """Return True if the coordinates fall within Bangladesh's bounding box."""
    s, w, n, e = _BANGLADESH_BBOX
    return s <= lat <= n and w <= lon <= e


def _build_overpass_query(latitude: float, longitude: float, query: str, radius: int = 15000) -> str:
    """Build an Overpass QL query restricted to Bangladesh's bounding box.

    The clauses target only mental-health related places, so general
    hospitals/clinics without a psychiatric speciality are excluded.
    """
    clauses = _OSM_CLAUSE_MAP.get(query, _OSM_CLAUSE_MAP["hospital"])
    s, w, n, e = _BANGLADESH_BBOX
    bbox = f"{s},{w},{n},{e}"

    body = "".join(
        f"{clause}(around:{radius},{latitude},{longitude});" for clause in clauses
    )

    return (
        f"[out:json][timeout:10][bbox:{bbox}];"
        f"({body});"
        f"out center 10;"
    )


def _extract_address(tags: dict) -> str:
    """Build an address string from OSM address tags."""
    parts = []
    housenumber = tags.get("addr:housenumber", "")
    street = tags.get("addr:street", "")
    if street:
        parts.append(f"{housenumber} {street}".strip())
    city = tags.get("addr:city", "")
    if city:
        parts.append(city)
    return ", ".join(parts) if parts else "Address not available"


def _extract_phone(tags: dict) -> str | None:
    """Extract phone number from OSM tags."""
    return tags.get("phone") or tags.get("contact:phone") or None


async def _search_overpass(latitude: float, longitude: float, query: str) -> list[dict]:
    """Search for nearby places using the free Overpass API (OpenStreetMap)."""
    overpass_query = _build_overpass_query(latitude, longitude, query)

    headers = {"User-Agent": "MentalHealthChatbot/1.0"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            _OVERPASS_URL,
            data={"data": overpass_query},
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    seen: set[tuple[str, str]] = set()
    for element in data.get("elements", []):
        if len(results) >= 5:
            break
        tags = element.get("tags", {})
        name = tags.get("name")
        if not name:
            continue

        osm_type = element.get("type", "node")
        osm_id = element.get("id", "")

        if (osm_type, str(osm_id)) in seen:
            continue
        seen.add((osm_type, str(osm_id)))

        if osm_type == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")

        if not lat or not lon or not _is_in_bangladesh(lat, lon):
            continue

        maps_link = f"https://www.openstreetmap.org/{osm_type}/{osm_id}"

        results.append({
            "name": name,
            "address": _extract_address(tags),
            "phone": _extract_phone(tags),
            "rating": None,
            "maps_link": maps_link,
        })
    return results


@tool
async def find_nearby_help(latitude: float, longitude: float, query: str = "hospital") -> str:
    """Find nearby hospitals, therapists, or mental health clinics based on location.

    Args:
        latitude: User's latitude coordinate.
        longitude: User's longitude coordinate.
        query: Type of help to search for — "hospital", "therapist", or "clinic".
    """
    query_lower = query.lower()

    try:
        places = await _search_overpass(latitude, longitude, query_lower)
        if places:
            lines = [f"Here are nearby {query_lower}s I found:\n"]
            for i, p in enumerate(places, 1):
                lines.append(f"{i}. **{p['name']}**")
                lines.append(f"   Address: {p['address']}")
                if p.get("phone"):
                    lines.append(f"   Phone: {p['phone']}")
                lines.append(f"   [View on Maps]({p['maps_link']})\n")
            return "\n".join(lines)
    except Exception:
        pass

    mock_key = query_lower if query_lower in _MOCK_DATA else "hospital"
    places = _MOCK_DATA[mock_key]
    lines = [f"Here are some {mock_key}s that may be helpful (sample data):\n"]
    for i, p in enumerate(places, 1):
        lines.append(f"{i}. **{p['name']}**")
        lines.append(f"   Address: {p['address']}")
        if p.get("phone"):
            lines.append(f"   Phone: {p['phone']}")
        if p.get("rating"):
            lines.append(f"   Rating: {p['rating']}/5")
        lines.append(f"   [View on Maps]({p['maps_link']})\n")
    lines.append("*Note: These are sample listings. For accurate results, please enable location services.*")
    return "\n".join(lines)
