---
name: gmb-places-lookup
display_name: "GMB Places Lookup"
description: "Search Google Places for a business by name (and optional address) and return qualification fields: hours, website, rating, review count, formatted address, place_id."
category: data
icon: map-pin
skill_type: sandbox
catalog_type: addon

resource_requirements:
  - env_var: GOOGLE_PLACES_API_KEY
    name: "Google Places API Key"
    description: "Get one at https://console.cloud.google.com/google/maps-apis/credentials. Enable Places API (New)."

tool_schema:
  name: gmb_places_lookup
  description: "Search Google Places for a business. Returns up to 5 candidate matches with the qualification fields needed for SDR onboarding (business hours, website, rating, user_ratings_total). Pass a `query` string with the business name; optionally include a city/address in `query` (e.g. 'Anna Coffee and Cookies, Brooklyn NY') to narrow when multiple results come back. The response is structured — the model should NOT show raw JSON to the lead."
  parameters:
    type: object
    properties:
      query:
        type: "string"
        description: "Business name (and optionally address/city) to search for, exactly as the lead provided it."
      language:
        type: "string"
        description: "ISO language code for results. Default 'en'."
    required: [query]
---

# Google Places Search

Wraps the Google Places API (New) `Text Search` endpoint. Returns the top 5 candidate businesses with the four fields needed for Jumper Media qualification:

- `regular_opening_hours` (presence indicates business hours are listed)
- `website_uri` (presence indicates website is configured)
- `rating` (the GMB star rating)
- `user_rating_count` (review count)

Plus identifiers (`place_id`, `display_name.text`, `formatted_address`) for confirming with the lead and for the onboarding form.

The skill normalizes the response so the calling agent can read `result.candidates[i].has_hours`, `has_website`, `rating`, `review_count` directly without re-parsing.
