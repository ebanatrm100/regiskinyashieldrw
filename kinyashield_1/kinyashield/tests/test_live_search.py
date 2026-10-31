import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import live_search as L
assert L.needs_live("What is the latest exchange rate of USD to RWF today?")
assert L.needs_live("Prix du maïs aujourd'hui") and L.needs_live("Igiciro cy'ibishyimbo uyu munsi") and L.needs_live("Habari za leo Rwanda")
assert not L.needs_live("what is a firewall") and not L.needs_live("my password is weak, what to do today")
assert isinstance(L.fetch("zzqq nothing", "en"), list)      # offline or empty: a list, never an exception
assert "Live sources" in L.sources_line([("T", "x", "https://a.b")], "en") and L.sources_line([], "en") == ""
print("OK live search")
