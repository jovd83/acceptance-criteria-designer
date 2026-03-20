# Invoice Export

As a finance manager, I want to export invoices to CSV so that accounting can reconcile them.

Rules:

- Only finalized invoices can be exported.
- The user must choose both a start date and an end date.
- The selected date range cannot exceed 31 days.
- When no finalized invoices match the range, the system still generates a CSV file with headers only.
