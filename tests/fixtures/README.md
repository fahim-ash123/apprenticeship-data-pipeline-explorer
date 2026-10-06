# Recorded API responses

These files were recorded from the live Explore Education Statistics API on 6 October 2026, for the apprenticeships headline data set `1d419801-a90e-f970-9335-a13623faccbe`. The tests replay them through a fake transport, so no test calls the live API.

- `summary.json` is the response from `/v1/data-sets/{id}`
- `versions.json` is the first page of `/v1/data-sets/{id}/versions`, with `pageSize=20`
- `data-set-head.csv` is the header and first five rows of `/v1/data-sets/{id}/csv` for version 2.0.2