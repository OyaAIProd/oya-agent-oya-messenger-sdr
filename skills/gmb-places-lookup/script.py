"""google-places — search Google Places API for a business and return qualification fields."""
import json
import os
import sys

import httpx


def main() -> None:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    if not api_key:
        print(json.dumps({"error": "GOOGLE_PLACES_API_KEY not set. Attach via: oya agent skills update <agent_id> google-places --credentials-json '{\"GOOGLE_PLACES_API_KEY\":\"...\"}'"}))
        sys.exit(1)

    query = (inp.get("query") or "").strip()
    if not query:
        print(json.dumps({"error": "query is required"}))
        sys.exit(1)

    language = inp.get("language") or "en"

    field_mask = ",".join([
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.regularOpeningHours",
        "places.websiteUri",
        "places.rating",
        "places.userRatingCount",
        "places.businessStatus",
        "places.location",
        "places.googleMapsUri",
    ])

    body = {
        "textQuery": query,
        "languageCode": language,
        "pageSize": 5,
    }

    try:
        with httpx.Client(timeout=30) as client:
            r = client.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": api_key,
                    "X-Goog-FieldMask": field_mask,
                },
                json=body,
            )
        if r.status_code != 200:
            print(json.dumps({
                "error": f"Google Places API returned {r.status_code}",
                "details": r.text[:500],
            }))
            sys.exit(1)

        data = r.json()
        places = data.get("places") or []

        candidates = []
        for p in places:
            hours = p.get("regularOpeningHours") or {}
            website = p.get("websiteUri") or ""
            rating = p.get("rating")
            review_count = p.get("userRatingCount") or 0
            display_name = (p.get("displayName") or {}).get("text", "")
            candidates.append({
                "place_id": p.get("id", ""),
                "name": display_name,
                "formatted_address": p.get("formattedAddress", ""),
                "google_maps_uri": p.get("googleMapsUri", ""),
                "business_status": p.get("businessStatus", ""),
                "has_hours": bool(hours.get("periods") or hours.get("weekdayDescriptions")),
                "has_website": bool(website),
                "website": website,
                "rating": rating,
                "review_count": review_count,
                "qualifies": (
                    bool(hours.get("periods") or hours.get("weekdayDescriptions"))
                    and bool(website)
                    and review_count >= 10
                    and (rating is not None and rating > 3.0)
                ),
                "disqualification_reasons": [
                    reason for reason, failed in [
                        ("no_hours", not bool(hours.get("periods") or hours.get("weekdayDescriptions"))),
                        ("no_website", not bool(website)),
                        ("fewer_than_10_reviews", review_count < 10),
                        ("rating_too_low", rating is None or rating <= 3.0),
                    ] if failed
                ],
            })

        result = {
            "ok": True,
            "query": query,
            "result_count": len(candidates),
            "candidates": candidates,
        }
        print(json.dumps(result))
    except httpx.HTTPError as e:
        print(json.dumps({"error": f"HTTP error: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
