import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import warmup, cyber_intel as ci
assert warmup.start() is True and warmup.start() is False         # one thread per process
# cyber search stops early when most sources have answered, and waits for slow ones only when too few did
import datetime as dt
p = {"start": dt.date(2026, 10, 1), "end": dt.date(2026, 10, 7), "key": "x"}
ci.EARLY_SECONDS, ci.TOTAL_TIMEOUT = 0.3, 1.0
def fast(): return ("feed", "<rss><channel></channel></rss>")
def slow(): time.sleep(2); return ("feed", "<rss><channel></channel></rss>")
jobs = [(f"f{i}", "news", ["security"], fast) for i in range(8)] + [("slow", "news", ["security"], slow)]
t = time.time(); r = ci._search(p, ["security"], "en", "", fetch_jobs=jobs); assert time.time() - t < 0.9 and "slow" in r["failed"]
jobs = [(f"f{i}", "news", ["security"], fast) for i in range(2)] + [("s1", "news", ["security"], slow), ("s2", "news", ["security"], slow)]
t = time.time(); r = ci._search(p, ["security"], "en", "", fetch_jobs=jobs); assert 0.9 < time.time() - t < 1.6
print("OK warmup")
