# What I checked, and what the agent got wrong

Write this yourself, in your own words. It is the part of the repo that proves the work is yours.

## What the agent got wrong

- I asked Bob to report what it found in the helper modules before fixing anything, but it fixed config_loader.py and log_util.py straight away. I only saw the problems listed after the changes were already made.
- Bob's final summary said the job was finished but didn't include the verify.py output. I ran python verify.py myself to confirm before trusting it.
- Bob changed split("=") to split("=", 1) in config_loader.py, which I hadn't asked for. I checked it and kept it, because it stops settings values containing "=" from breaking, but I had to read it to know it was safe.

## What I checked before I accepted its work

WHAT BROKE
The service check never warned about a car until it had already gone past its full 15,000 km interval. Wear was worked out with whole-number division, so a car at 14,900 km showed 0% instead of about 99%, and it was never flagged at the 80% threshold. The same mistake made the fleet report show average wear as 0.00 instead of about 59.67. A car with no last-service reading crashed the nightly report and was wrongly flagged. The report also converted kilometres to miles the wrong way round, so 100 km showed as 160.9 miles instead of about 62.1.

WHY IT WAS DANGEROUS
The script checks about 6,000 cars every night, and no car ever got an early warning. Every car went past its service interval silently, which means more overdue services, more breakdowns on the road, and more money spent on emergency repairs and downtime. The report gave no error and just said everything was fine, so nobody had a reason to doubt it. One car with a missing reading could crash the whole nightly report, so the entire fleet would go unchecked that night. The wrong mileage figures would also mislead anyone reading the report in miles.

WHAT I CHANGED
- Wear now uses normal division (/) instead of floor division (//), so 14,900 km reads 99.3% and is flagged. Same fix in the fleet average, which now reads about 59.67.
- A car with no last-service reading is no longer counted as 0 km and no longer crashes the report. It is skipped safely.
- Fixed the km-to-miles constant from 1.609 to 0.621371 (the old value was the conversion for miles to km).
- Small cleanups in the helper modules: proper "is None" checks, files opened with "with", and safer parsing of settings lines.
- Added tests for wear at 79%, 80%, 81% and 14,900 km, plus a test that a car with no reading doesn't crash the report.
- The 15,000 km interval and the 80% threshold are unchanged, in both the code and settings.cfg.
Proof: all tests pass with python -m pytest -v, and python verify.py passes. I reviewed every change with git diff before committing.

## What the data actually said
Total km and age were almost the same in both groups, so they don't explain breakdowns. The cars that broke down had driven much further since their last service (11,677 vs 7,261 km) and were used harder. I trusted these columns because the gap was large and consistent. With only 26 breakdowns, this shows a link, not proof of cause.
