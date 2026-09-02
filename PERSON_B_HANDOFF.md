# Team 2 Person A → Person B Handoff

## 1. Purpose

Person A provides the probable source trajectory and source corridor
for a detected oil spill.

Person B uses these outputs together with AIS data to identify and rank
vessels that could be associated with the spill.

---

## 2. API Endpoint

### POST

https://petite-fingers-inspections-feed.trycloudflare.com/hindcast

> This is a temporary development Cloudflare URL.
> It may change when the tunnel is restarted.

---

## 3. Request

Send the Team 1 detection JSON to `/hindcast`.

Example:

```json
{
  "incident_id": "INC001",
  "centroid": [
    54.48877510459397,
    25.322134857980192
  ],
  "detection_time": "2026-09-01T20:45:15.466871Z",
  "spill_geojson": {}
}