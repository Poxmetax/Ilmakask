# Ilma Kask studio

- influencer.json: the bible. Read at session start, update at session end.
- ledger.csv: one row per tool and per asset. commercial_ok must be yes, watermark no,
  verified_on recent, and derived_from lists upstream asset_ids (separated by ;).
- publish/queue: one folder per post; run license_gate.py before publishing.
