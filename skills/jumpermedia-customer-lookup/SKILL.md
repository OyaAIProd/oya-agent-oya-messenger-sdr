---
name: jumpermedia-customer-lookup
display_name: "Jumper Media Customer Lookup"
description: "Query the Jumper Media customer database (via Xano) to check if a lead is a returning or current customer. Looks up by GMB name and/or email; returns subscription status (none / inactive / active) so the SDR agent can branch."
category: data
icon: user-search
skill_type: sandbox
catalog_type: addon

resource_requirements:
  - env_var: JUMPERMEDIA_XANO_BASE_URL
    name: "Jumper Media Xano Base URL"
    description: "Base URL of the Xano API for Jumper Media (e.g. https://x8ki-letl-twmt.n7.xano.io/api:abc123). The endpoint /customer-lookup is appended."
  - env_var: JUMPERMEDIA_XANO_AUTH_TOKEN
    name: "Jumper Media Xano Auth Token"
    description: "Bearer token or API key Xano expects. Sent as 'Authorization: Bearer <token>'. Leave blank if the endpoint is public."

tool_schema:
  name: jumpermedia_customer_lookup
  description: "Look up a Jumper Media lead in the customer database BEFORE running the full onboarding flow. Pass the lead's GMB business name and/or email. Returns: {found: bool, status: 'none'|'active'|'inactive', user: {...} | null}. Use 'inactive' to send the reactivation Calendly link; use 'active' to send the existing-account login message; use 'none' to continue with onboarding."
  parameters:
    type: object
    properties:
      gmb_name:
        type: "string"
        description: "Confirmed GMB business name from Google Places (formatted_address can also be passed via gmb_address). Pass empty string if not yet known."
        default: ""
      gmb_address:
        type: "string"
        description: "Confirmed GMB formatted address from Google Places. Helps disambiguate when names collide."
        default: ""
      email:
        type: "string"
        description: "Lead's email address, once collected. Pass empty string if not yet collected."
        default: ""
    required: []
---

# Jumper Media Customer Lookup

Hits the Jumper Media Xano customer endpoint to determine if the inbound Messenger lead is:

- `none` — never been a customer. Continue with onboarding.
- `inactive` — was a paying customer, currently lapsed. Send the reactivation Calendly link instead of onboarding.
- `active` — currently has a paid subscription (matched on email OR gmb). Send "you already have an account" message with login link + support email.

The endpoint accepts any combination of `gmb_name`, `gmb_address`, and `email` and matches on whatever is provided. The skill returns a clean status field so the agent doesn't need to reinterpret raw Xano rows.

If the endpoint is unreachable or auth fails, the skill returns `{ok: false, error: "..."}` — the agent should treat that as `status: "none"` and continue cautiously rather than blocking the lead.
