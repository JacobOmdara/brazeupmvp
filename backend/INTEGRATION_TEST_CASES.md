# Integration Test Cases

## Test 1: Submit Full Inspection Form
- Endpoint: POST /api/submit-inspection
- Input: part_family=H, alloy=jh, damage_type=jgh, gap_estimate=1mm, length_estimate=20mm, consent=true, photos=[img1, img2]
- Expected: 200 OK, submission_id returned

## Test 2: Get All Cases
- Endpoint: GET /api/cases
- Expected: 200 OK, array of all inspection cases

## Test 3: Get Specific Case
- Endpoint: GET /api/cases/{case_id}
- Expected: 200 OK, case details with status

## Test 4: Update Case Status
- Endpoint: PATCH /api/cases/{case_id}/status
- Input: new status (pending, completed, rejected)
- Expected: 200 OK, status updated

## Edge Cases
- Submit without photos → Should reject
- Invalid case_id → Should return 404
- Missing required fields → Should return 400