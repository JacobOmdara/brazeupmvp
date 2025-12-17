# Abdul's Frontend Task

Build a web form that connects to BrazeUp API

## Requirements

1. **Upload form** — Accept photos (drag-drop or file input)
2. **POST /api/upload** — Send files, get upload_id
3. **POST /api/analyze** — Use upload_id, get defects
4. **Display results** — Table: Type | Confidence | Bounding Box
5. **Inspection form** — Part Family, Alloy, Damage Type, Gap (mm), Length (mm), Consent
6. **POST /api/submit-inspection** — Submit form, get case_id

## Tech

- React, Vue, or vanilla HTML/JS
- Fetch API or Axios
- Base URL: http://localhost:5000

## References

- API_DOCS.md — Endpoint specs
- FRONTEND_INTEGRATION_GUIDE.md — Response formats
- SETUP.md — Backend setup

## Deliverables

- Working form (HTML/React/Vue)
- All 3 endpoints working
- Error handling
- Push to GitHub
