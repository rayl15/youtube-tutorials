"""Pre-refactor: FAILS. Post-refactor: PASSES.

The agent's job:
1. Add `logging.getLogger(__name__)` to each of auth.py, db.py, api.py, utils.py.
2. Add at least one `logger.info(...)` call inside one function in each module.
3. Run this test to verify.
"""
from pathlib import Path

MODULES = ["auth.py", "db.py", "api.py", "utils.py"]


def main():
    here = Path(__file__).parent
    failures = []
    for m in MODULES:
        src = (here / m).read_text()
        if "logging.getLogger" not in src:
            failures.append(f"{m}: missing `logging.getLogger(__name__)`")
        if "logger.info(" not in src:
            failures.append(f"{m}: missing `logger.info(...)` call")
    if failures:
        for f in failures:
            print(f"FAIL  {f}")
        raise SystemExit(1)
    print(f"PASS  All {len(MODULES)} modules have logging wired up.")


if __name__ == "__main__":
    main()
