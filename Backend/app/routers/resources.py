from fastapi import APIRouter, HTTPException, Query

from app.schemas import CrisisLine, CrisisLinesResponse, NearbyPlace, NearbyResponse
from app.services.crisis_service import CRISIS_HOTLINES

router = APIRouter(prefix="/api/v1/resources", tags=["resources"])


@router.get("/nearby", response_model=NearbyResponse)
async def get_nearby_resources(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    type: str = Query(default="hospital", pattern="^(hospital|therapist|clinic)$"),
):
    from app.tools.location import _search_overpass, _MOCK_DATA, _is_in_bangladesh

    if not _is_in_bangladesh(latitude, longitude):
        raise HTTPException(
            status_code=400,
            detail=(
                "Coordinates are outside Bangladesh. "
                "This service only supports locations within Bangladesh "
                "(latitude 20.7–26.6, longitude 88.0–92.7)."
            ),
        )

    try:
        real_places = await _search_overpass(latitude, longitude, type)
        if real_places:
            places = [
                NearbyPlace(
                    name=p["name"],
                    address=p["address"],
                    phone=p.get("phone"),
                    rating=p.get("rating"),
                    maps_link=p["maps_link"],
                )
                for p in real_places
            ]
            return NearbyResponse(places=places, source="openstreetmap")
    except Exception:
        pass

    mock_key = type if type in _MOCK_DATA else "hospital"
    places = [
        NearbyPlace(
            name=p["name"],
            address=p["address"],
            phone=p.get("phone"),
            rating=p.get("rating"),
            maps_link=p["maps_link"],
        )
        for p in _MOCK_DATA[mock_key]
    ]
    return NearbyResponse(places=places, source="mock")


@router.get("/crisis-lines", response_model=CrisisLinesResponse)
async def get_crisis_lines():
    return CrisisLinesResponse(
        crisis_lines=[
            CrisisLine(
                name=h["name"],
                contact=h["contact"],
                description=h["description"],
                available=h["available"],
            )
            for h in CRISIS_HOTLINES
        ]
    )