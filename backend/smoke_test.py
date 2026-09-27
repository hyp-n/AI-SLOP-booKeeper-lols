"""End-to-end smoke test against a running backend. Run: python smoke_test.py"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://localhost:5000/api"
FAILS = []


def req(method, path, body=None, token=None, expect=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            raw = resp.read().decode()
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        status = e.code
    except Exception as e:
        print(f"  !! {method} {path} -> connection error: {e}")
        FAILS.append(f"{method} {path} connection error")
        return None, 0

    try:
        parsed = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        parsed = raw

    ok = "ok " if (expect is None or status == expect) else "FAIL"
    if expect is not None and status != expect:
        FAILS.append(f"{method} {path} -> {status} (want {expect}): {str(parsed)[:200]}")
    print(f"  [{ok}] {method:6} {path:52} {status}")
    return parsed, status


def check(label, cond, detail=""):
    if cond:
        print(f"  [ok ] {label}")
    else:
        print(f"  [FAIL] {label} {detail}")
        FAILS.append(f"{label} {detail}")


stamp = str(int(time.time()))
A = {"email": f"alice{stamp}@test.com", "password": "secret123", "name": "Alice"}
B = {"email": f"bob{stamp}@test.com", "password": "secret123", "name": "Bob"}

print("\n=== AUTH ===")
ra, _ = req("POST", "/auth/register", A, expect=201)
check("register returns token", bool(ra and ra.get("token")))
check("register user email", ra and ra["user"]["email"] == A["email"])
check("password hash not leaked", "password_hash" not in json.dumps(ra or {}))

req("POST", "/auth/register", A, expect=409)  # duplicate
req("POST", "/auth/register", {"email": "x@y.com", "password": "1"}, expect=400)  # short pw
rl, _ = req("POST", "/auth/login", {"email": A["email"], "password": A["password"]}, expect=200)
req("POST", "/auth/login", {"email": A["email"], "password": "wrong"}, expect=401)
# case-insensitive email
rl2, _ = req("POST", "/auth/login", {"email": A["email"].upper(), "password": A["password"]}, expect=200)
check("login is case-insensitive on email", bool(rl2 and rl2.get("token")))

rb, _ = req("POST", "/auth/register", B, expect=201)
ta, tb = ra["token"], rb["token"]
ida, idb = ra["user"]["id"], rb["user"]["id"]

req("GET", "/auth/me", token=ta, expect=200)
req("GET", "/auth/me", expect=401)  # no token
req("GET", "/auth/me", token="garbage", expect=401)  # bad token
up, _ = req("PUT", "/auth/me", {"name": "Alice B", "bio": "reader of many things"}, ta, expect=200)
check("update me", up and up["name"] == "Alice B")

print("\n=== BOOKS ===")
book, _ = req("POST", "/books/", {"title": "Dune", "author": "Frank Herbert", "page_count": 412}, expect=201)
check("book created", bool(book and book.get("id")))
req("POST", "/books/", {"author": "no title"}, expect=400)
req("GET", "/books/", expect=200)
req("GET", f"/books/{book['id']}", expect=200)
req("GET", "/books/000000000000000000000000", expect=404)  # valid oid, missing
req("GET", "/books/not-an-oid", expect=404)  # invalid oid must not 500
gb, _ = req("POST", "/books/", {"title": "Dune", "isbn": "9780441013593"}, expect=201)
req("POST", "/books/", {"title": "Dune Dup", "isbn": "9780441013593"}, expect=409)  # dup isbn

print("\n=== READING ===")
pr, _ = req("PUT", f"/reading/{book['id']}", {"current_page": 100, "status": "reading"}, expect=200)
check("percentage calc", pr and abs(pr["percentage"] - 24.3) < 0.2, f"got {pr and pr.get('percentage')}")
check("status set", pr and pr["status"] == "reading")
pr2, _ = req("PUT", f"/reading/{book['id']}", {"current_page": 412}, expect=200)
check("auto-finish at 100%", pr2 and pr2["status"] == "finished", f"got {pr2 and pr2.get('status')}")
req("GET", f"/reading/{book['id']}", expect=200)
stats, _ = req("GET", "/reading/stats", expect=200)
check("stats present", stats and "total_books" in stats)

print("\n=== COLLECTIONS ===")
c, _ = req("POST", "/collections/", {"name": "Sci-Fi"}, expect=201)
req("POST", "/collections/", {"name": ""}, expect=400)
c2, _ = req("POST", "/collections/", {"name": "Classics"}, expect=201)
check("order_index increments", c2["order_index"] == c["order_index"] + 1)
req("POST", f"/collections/{c['id']}/books", {"book_id": book["id"]}, expect=201)
req("POST", f"/collections/{c['id']}/books", {"book_id": book["id"]}, expect=409)  # already in
req("POST", f"/collections/{c['id']}/books", {"book_id": "000000000000000000000000"}, expect=404)
got, _ = req("GET", f"/collections/{c['id']}", expect=200)
check("collection has book", got and len(got.get("books", [])) == 1)
req("PUT", f"/collections/{c['id']}/reorder", {"book_ids": [book["id"]]}, expect=200)
req("DELETE", f"/collections/{c['id']}/books/{book['id']}", expect=200)
got2, _ = req("GET", f"/collections/{c['id']}", expect=200)
check("book removed from collection", got2 and len(got2.get("books", [])) == 0)

print("\n=== SOCIAL ===")
req("GET", "/social/friends", token=ta, expect=200)
fr, _ = req("POST", "/social/friends/request", {"email": A["email"]}, ta, expect=400)  # self
req("POST", "/social/friends/request", {"email": "nobody@nowhere.com"}, ta, expect=404)
freq, _ = req("POST", "/social/friends/request", {"email": B["email"]}, ta, expect=201)
req("POST", "/social/friends/request", {"email": B["email"]}, ta, expect=409)  # dup
req("POST", "/social/friends/request", {"email": A["email"]}, tb, expect=409)  # reverse pending
req("PUT", f"/social/friends/accept/{freq['id']}", token=tb, expect=403)  # wrong receiver
req("PUT", f"/social/friends/accept/{freq['id']}", token=ta, expect=200)  # sender accepting = wrong too
req("PUT", f"/social/friends/accept/{freq['id']}", token=tb, expect=200)
friends, _ = req("GET", "/social/friends", token=ta, expect=200)
check("friend is accepted", friends and len(friends) == 1, f"got {len(friends or [])}")
s, _ = req("GET", f"/social/users/search?q=alice{stamp}", token=tb, expect=200)
check("search finds alice", s and any(u["email"] == A["email"] for u in s))
check("search excludes self", s and all(u["id"] != idb for u in s))

# currently reading on profile
req("PUT", "/auth/me", {"currently_reading": book["id"]}, ta, expect=200)
prof, _ = req("GET", f"/social/users/{idb}", token=ta, expect=200)
prof2, _ = req("GET", f"/social/users/{ida}", token=tb, expect=200)
check("profile shows currently reading", prof2 and prof2.get("currently_reading_book"), )
check("profile friendship accepted", prof2 and prof2.get("friendship_status") == "accepted")
req("GET", "/social/users/000000000000000000000000", token=ta, expect=404)
req("DELETE", f"/social/friends/{idb}", token=ta, expect=200)
friends2, _ = req("GET", "/social/friends", token=ta, expect=200)
check("friend removed", friends2 and len(friends2) == 0)

# re-friend for messaging
req("POST", "/social/friends/request", {"email": B["email"]}, ta, expect=201)
req("GET", "/social/friends/requests", token=tb, expect=200)

print("\n=== MESSAGES ===")
conv, _ = req("POST", "/messages/conversations", {"participant_ids": [idb]}, ta, expect=201)
check("conversation created", conv and conv.get("id"))
conv_again, _ = req("POST", "/messages/conversations", {"participant_ids": [idb]}, ta, expect=200)
check("1-on-1 dedupe", conv_again and conv_again["id"] == conv["id"])
req("GET", f"/messages/conversations/{conv['id']}/messages", token=tb, expect=200)  # not yet friends but member
m1, _ = req("POST", f"/messages/conversations/{conv['id']}/messages", {"content": "hey bob"}, ta, expect=201)
check("message sender is alice", m1 and m1["sender"] == ida)
req("POST", f"/messages/conversations/{conv['id']}/messages", {"content": "   "}, ta, expect=400)
req("GET", f"/messages/conversations/{conv['id']}/messages", token=ta, expect=200)
req("GET", f"/messages/conversations/{conv['id']}/messages", expect=401)

# third user not in conversation
rc, _ = req("POST", "/auth/register", {"email": f"carol{stamp}@test.com", "password": "secret123", "name": "Carol"}, expect=201)
tc, idc = rc["token"], rc["user"]["id"]
req("GET", f"/messages/conversations/{conv['id']}/messages", token=tc, expect=403)
req("POST", f"/messages/conversations/{conv['id']}/messages", {"content": "sneak"}, tc, expect=403)

grp, _ = req("POST", "/messages/conversations", {"participant_ids": [idb, idc], "is_group": True, "group_name": "Book Club"}, ta, expect=201)
check("group created", grp and grp["is_group"] and grp["group_name"] == "Book Club")
req("PUT", f"/messages/conversations/{grp['id']}/group/rename", {"name": "Readers"}, token=tb, expect=403)  # not admin
req("PUT", f"/messages/conversations/{grp['id']}/group/rename", {"name": "Readers"}, token=ta, expect=200)
req("POST", f"/messages/conversations/{grp['id']}/group/add", {"user_id": idb}, token=ta, expect=200)  # already member
req("PUT", f"/messages/conversations/{grp['id']}/group/rename", {"name": ""}, token=ta, expect=400)
convs, _ = req("GET", "/messages/conversations", token=ta, expect=200)
check("alice sees 2 convs", convs and len(convs) == 2, f"got {len(convs or [])}")
check("conv has participant_details", convs and all("participant_details" in c for c in convs))
check("conv has last_message", convs and any(c.get("last_message") for c in convs))

print("\n=== CLEANUP ===")
req("DELETE", f"/books/{book['id']}", expect=200)
req("DELETE", f"/books/{book['id']}", expect=404)
req("DELETE", f"/collections/{c2['id']}", expect=200)

print("\n" + "=" * 60)
if FAILS:
    print(f"{len(FAILS)} FAILURES:")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("ALL PASSED")
