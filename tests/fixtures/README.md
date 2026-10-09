# Recorded API responses

These files were recorded from the live Explore Education Statistics API for the apprenticeships headline data set `1d419801-a90e-f970-9335-a13623faccbe`. The tests replay them through a fake transport or read them directly, so no test calls the live API.

- `summary.json` is the response from `/v1/data-sets/{id}`, recorded on 6 October 2026
- `versions.json` is the first page of `/v1/data-sets/{id}/versions`, with `pageSize=20`, recorded on 6 October 2026
- `data-set-head.csv` is the header and first five rows of `/v1/data-sets/{id}/csv` for version 2.0.2, recorded on 6 October 2026
- `meta-1.0.json`, `meta-1.0.1.json` and `meta-2.0.2.json` are the filters and indicators from `/v1/data-sets/{id}/meta` for those versions, recorded on 8 October 2026, with locations and time periods removed to keep them small
- `national-totals.csv` is the national grand total row for each year, every filter set to `Total`, taken from the version 2.0.2 CSV on 8 October 2026, in the order the API returned them
- `national-breakdowns.csv` is every national row from the version 2.0.2 CSV that breaks starts down by one filter with the others at `Total`, plus the age rows with their matching youth or adult value, taken on 8 October 2026
- `regional-levels.csv` is every regional row from the version 2.0.2 CSV with every filter at `Total` apart from the apprenticeship level, giving each region's total starts and its starts by level, taken on 8 October 2026