import os

# Must be set before `haystack` is imported anywhere in the app (Haystack
# reads this at import time), per SECURITY_AND_DATA.md's "disable framework
# telemetry" requirement. docker-compose.yml also sets this explicitly for
# the container; this covers local/non-Docker runs and tests too.
os.environ.setdefault("HAYSTACK_TELEMETRY_ENABLED", "False")
