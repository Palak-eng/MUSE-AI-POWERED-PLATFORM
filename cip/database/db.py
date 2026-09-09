"""SQLite persistence layer.

Swap for Postgres/Supabase by replacing _conn() and the SQL statements.
Every function signature stays the same — pages never touch raw SQL.
"""
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import os

_old_default = Path(__file__).parent.parent.parent / "musely.db"
_new_default = Path(__file__).parent.parent.parent / "muse.db"


def _resolve_db_path() -> Path:
    """Prefer muse.db; fall back to musely.db if it already exists."""
    env = os.environ.get("DB_PATH", "").strip()
    if env:
        return Path(env)
    if _new_default.exists():
        return _new_default
    if _old_default.exists():
        return _old_default
    return _new_default


DB_PATH = _resolve_db_path()

@contextmanager
def _conn():
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    """Create all tables (idempotent)."""
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                avatar        TEXT    DEFAULT '✨',
                plan          TEXT    DEFAULT 'free',
                onboarded     INTEGER DEFAULT 0,
                created_at    TEXT    DEFAULT (datetime('now')),
                updated_at    TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS creator_profiles (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER UNIQUE REFERENCES users(id),
                bio           TEXT DEFAULT '',
                username      TEXT DEFAULT '',
                niche         TEXT DEFAULT '',
                platforms     TEXT DEFAULT '[]',
                followers     TEXT DEFAULT '',
                engagement    TEXT DEFAULT '',
                age_range     TEXT DEFAULT '',
                gender_split  TEXT DEFAULT '',
                geography     TEXT DEFAULT '',
                tone          TEXT DEFAULT '[]',
                past_brands   TEXT DEFAULT '',
                no_go         TEXT DEFAULT '',
                recent_posts  TEXT DEFAULT '',
                goals         TEXT DEFAULT '',
                content_style TEXT DEFAULT '',
                updated_at    TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS saved_reports (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER REFERENCES users(id),
                type       TEXT NOT NULL,
                title      TEXT NOT NULL,
                content    TEXT NOT NULL,
                status     TEXT DEFAULT 'saved',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS deals (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER REFERENCES users(id),
                brand          TEXT NOT NULL,
                deal_value     REAL DEFAULT 0,
                status         TEXT DEFAULT 'Pending',
                deliverables   TEXT DEFAULT '',
                campaign_date  TEXT DEFAULT '',
                payment_status TEXT DEFAULT 'Pending',
                notes          TEXT DEFAULT '',
                engagement     REAL DEFAULT 0,
                created_at     TEXT DEFAULT (datetime('now'))
            );
        """)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash(pw: str) -> str:
    """Hash with PBKDF2-HMAC-SHA256 + random salt. Format: pbkdf2$<salt>$<hash>."""
    import secrets as _secrets

    salt = _secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), 200_000)
    return f"pbkdf2${salt}${dk.hex()}"


def _verify(pw: str, stored: str) -> bool:
    """Verify against new pbkdf2 format, with fallback to legacy plain sha256."""
    if not stored:
        return False
    if stored.startswith("pbkdf2$"):
        try:
            _, salt_hex, hash_hex = stored.split("$", 2)
            dk = hashlib.pbkdf2_hmac(
                "sha256", pw.encode("utf-8"), bytes.fromhex(salt_hex), 200_000
            )
            import hmac as _hmac

            return _hmac.compare_digest(dk.hex(), hash_hex)
        except Exception:
            return False
    # Legacy: plain sha256 hex (pre-hardening accounts) — still accept.
    import hmac as _hmac

    legacy = hashlib.sha256(pw.encode("utf-8")).hexdigest()
    return _hmac.compare_digest(legacy, stored)


# ── Users ─────────────────────────────────────────────────────────────────────

def create_user(name: str, email: str, password: str):
    """Return new user dict, or None if email already taken."""
    try:
        with _conn() as con:
            cur = con.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?,?,?)",
                (name.strip(), email.strip().lower(), _hash(password)),
            )
            uid = cur.lastrowid
            con.execute("INSERT INTO creator_profiles (user_id) VALUES (?)", (uid,))
        return get_user_by_id(uid)
    except sqlite3.IntegrityError:
        return None


def get_user_by_email(email: str):
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM users WHERE email=?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(uid: int):
    with _conn() as con:
        row = con.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None


def verify_password(email: str, password: str):
    user = get_user_by_email(email)
    if user and _verify(password, user["password_hash"]):
        return user
    return None


def mark_onboarded(uid: int):
    with _conn() as con:
        con.execute(
            "UPDATE users SET onboarded=1, updated_at=? WHERE id=?",
            (datetime.now().isoformat(), uid),
        )


def update_user_name(uid: int, name: str):
    update_user_account(uid, name, None)


def update_user_account(uid: int, name: str | None = None, avatar: str | None = None):
    """Update display name and/or avatar emoji. None = leave unchanged."""
    fields, vals = [], []
    if name is not None and name.strip():
        fields.append("name=?")
        vals.append(name.strip())
    if avatar is not None:
        fields.append("avatar=?")
        vals.append(avatar)
    if not fields:
        return
    vals.append(datetime.now().isoformat())
    vals.append(uid)
    with _conn() as con:
        con.execute(
            f"UPDATE users SET {', '.join(fields)}, updated_at=? WHERE id=?",
            tuple(vals),
        )


# ── Creator Profiles ──────────────────────────────────────────────────────────

def get_profile(uid: int) -> dict:
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM creator_profiles WHERE user_id=?", (uid,)
        ).fetchone()
        if not row:
            return {}
        d = dict(row)
        for _key in ("platforms", "tone"):
            try:
                val = d.get(_key) or "[]"
                parsed = json.loads(val) if isinstance(val, str) else val
                d[_key] = parsed if isinstance(parsed, list) else []
            except Exception:
                d[_key] = []
        return d


def save_profile(uid: int, data: dict):
    p = {
        "user_id": uid,
        "bio": data.get("bio", ""),
        "username": data.get("username", ""),
        "niche": data.get("niche", ""),
        "platforms": json.dumps(data.get("platforms", [])),
        "followers": data.get("followers", ""),
        "engagement": data.get("engagement", ""),
        "age_range": data.get("age_range", ""),
        "gender_split": data.get("gender_split", ""),
        "geography": data.get("geography", ""),
        "tone": json.dumps(data.get("tone", [])),
        "past_brands": data.get("past_brands", ""),
        "no_go": data.get("no_go", ""),
        "recent_posts": data.get("recent_posts", ""),
        "goals": data.get("goals", ""),
        "content_style": data.get("content_style", ""),
        "updated_at": datetime.now().isoformat(),
    }
    with _conn() as con:
        con.execute("""
            INSERT INTO creator_profiles
                (user_id,bio,username,niche,platforms,followers,engagement,
                 age_range,gender_split,geography,tone,past_brands,no_go,
                 recent_posts,goals,content_style,updated_at)
            VALUES
                (:user_id,:bio,:username,:niche,:platforms,:followers,:engagement,
                 :age_range,:gender_split,:geography,:tone,:past_brands,:no_go,
                 :recent_posts,:goals,:content_style,:updated_at)
            ON CONFLICT(user_id) DO UPDATE SET
                bio=excluded.bio, username=excluded.username,
                niche=excluded.niche, platforms=excluded.platforms,
                followers=excluded.followers, engagement=excluded.engagement,
                age_range=excluded.age_range, gender_split=excluded.gender_split,
                geography=excluded.geography, tone=excluded.tone,
                past_brands=excluded.past_brands, no_go=excluded.no_go,
                recent_posts=excluded.recent_posts, goals=excluded.goals,
                content_style=excluded.content_style, updated_at=excluded.updated_at
        """, p)


# ── Reports / Library ─────────────────────────────────────────────────────────

def save_report(uid: int, rtype: str, title: str, content: str) -> int:
    with _conn() as con:
        row = con.execute(
            "SELECT id FROM saved_reports WHERE user_id=? AND title=?", (uid, title)
        ).fetchone()
        if row:
            con.execute(
                "UPDATE saved_reports SET content=?, type=?, created_at=? WHERE id=?",
                (content, rtype, datetime.now().isoformat(), row["id"]),
            )
            return row["id"]
        cur = con.execute(
            "INSERT INTO saved_reports (user_id, type, title, content) VALUES (?,?,?,?)",
            (uid, rtype, title, content),
        )
        return cur.lastrowid


def get_reports(uid: int) -> list:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM saved_reports WHERE user_id=? ORDER BY created_at DESC",
            (uid,),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_report(report_id: int, uid: int):
    with _conn() as con:
        con.execute(
            "DELETE FROM saved_reports WHERE id=? AND user_id=?", (report_id, uid)
        )


# ── Deals ─────────────────────────────────────────────────────────────────────

def _safe_num(value, default: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def create_deal(uid: int, deal: dict) -> int:
    with _conn() as con:
        cur = con.execute(
            """INSERT INTO deals
               (user_id,brand,deal_value,status,deliverables,
                campaign_date,payment_status,notes,engagement)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                uid,
                deal.get("brand", ""),
                _safe_num(deal.get("deal_value", 0)),
                deal.get("status", "Pending"),
                deal.get("deliverables", ""),
                str(deal.get("campaign_date", "")),
                deal.get("payment_status", "Pending"),
                deal.get("notes", ""),
                _safe_num(deal.get("engagement", 0)),
            ),
        )
        return cur.lastrowid


def get_deals(uid: int) -> list:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM deals WHERE user_id=? ORDER BY created_at DESC", (uid,)
        ).fetchall()
        return [dict(r) for r in rows]


def delete_deal(deal_id: int, uid: int):
    with _conn() as con:
        con.execute("DELETE FROM deals WHERE id=? AND user_id=?", (deal_id, uid))
