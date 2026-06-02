"""Helper utilities: TOTP generation and Random profile generation."""
from __future__ import annotations

import random
import re
import secrets
import string
import time
from datetime import datetime

import pyotp


# ──────────────────────────────────────────────────────────────────────────
# TOTP Helpers
# ──────────────────────────────────────────────────────────────────────────

_BASE32_RE = re.compile(r"^[A-Z2-7]+=*$")


class TotpError(Exception):
    """TOTP fail."""


def normalize_secret(raw: str) -> str:
    """Chuẩn hoá secret: bỏ space, uppercase. Reject ký tự invalid."""
    s = (raw or "").strip().replace(" ", "").replace("-", "").upper()
    if not s:
        raise TotpError("secret rỗng")
    if not _BASE32_RE.match(s):
        raise TotpError(f"secret chứa ký tự không phải base32: {s!r}")
    return s


def generate_code(secret: str, *, at: float | None = None) -> str:
    """Generate 6-digit TOTP code.

    Args:
        secret: base32 secret từ /mfa/enroll.
        at: unix timestamp. None = now.

    Returns: 6-digit string.
    """
    sec = normalize_secret(secret)
    totp = pyotp.TOTP(sec)
    if at is None:
        return totp.now()
    return totp.at(at)


def time_remaining(*, at: float | None = None) -> int:
    """Số giây còn lại đến lúc code hiện tại expire (TOTP step = 30s)."""
    t = at if at is not None else time.time()
    return 30 - int(t) % 30


def provisioning_uri(secret: str, *, account: str, issuer: str = "ChatGPT") -> str:
    """`otpauth://` URI để cài vào Google Authenticator/Authy."""
    sec = normalize_secret(secret)
    return pyotp.TOTP(sec).provisioning_uri(name=account, issuer_name=issuer)


def verify_code(secret: str, code: str, *, valid_window: int = 1) -> bool:
    """Kiểm tra code có khớp với secret không.

    `valid_window=1` cho phép code của cửa sổ trước/sau (clock skew tolerance).
    """
    sec = normalize_secret(secret)
    return pyotp.TOTP(sec).verify(code, valid_window=valid_window)


# ──────────────────────────────────────────────────────────────────────────
# Random Profile Generator
# ──────────────────────────────────────────────────────────────────────────

# First names + last names — pool đủ rộng, common names US/EU
_FIRST_NAMES = (
    "Aaron", "Adam", "Alex", "Alexander", "Andrew", "Anthony", "Asher", "Austin",
    "Benjamin", "Blake", "Brandon", "Brian", "Caleb", "Cameron", "Carter", "Charles",
    "Christian", "Christopher", "Cody", "Cole", "Colton", "Connor", "Daniel", "David",
    "Dean", "Dominic", "Dylan", "Easton", "Edward", "Elijah", "Eric", "Ethan",
    "Evan", "Felix", "Gabriel", "Gavin", "George", "Grayson", "Henry", "Hudson",
    "Hunter", "Ian", "Isaac", "Isaiah", "Jack", "Jackson", "Jacob", "James",
    "Jason", "Jeremy", "Joel", "John", "Jonathan", "Jordan", "Joseph", "Joshua",
    "Julian", "Justin", "Kevin", "Kyle", "Landon", "Leo", "Levi", "Liam",
    "Logan", "Lucas", "Luke", "Mark", "Matthew", "Max", "Mason", "Michael",
    "Miles", "Nathan", "Nicholas", "Noah", "Oliver", "Owen", "Parker", "Patrick",
    "Paul", "Peter", "Philip", "Quinn", "Reid", "Robert", "Ryan", "Samuel",
    "Sean", "Sebastian", "Simon", "Steven", "Thomas", "Timothy", "Tyler", "Vincent",
    "Wesley", "William", "Wyatt", "Xavier", "Zachary", "Zane",
    "Ava", "Amelia", "Aria", "Aurora", "Avery", "Bella", "Brooklyn", "Camila",
    "Charlotte", "Chloe", "Claire", "Eleanor", "Elena", "Eliana", "Elizabeth",
    "Ella", "Ellie", "Emily", "Emma", "Evelyn", "Gianna", "Grace", "Hannah",
    "Harper", "Hazel", "Isabella", "Isla", "Ivy", "Julia", "Kennedy", "Layla",
    "Leah", "Lila", "Lily", "Lucy", "Luna", "Madison", "Mia", "Mila",
    "Naomi", "Natalie", "Nora", "Olivia", "Penelope", "Riley", "Ruby", "Sadie",
    "Sarah", "Savannah", "Scarlett", "Sofia", "Sophia", "Stella", "Valentina",
    "Victoria", "Violet", "Willow", "Zoe",
)

_LAST_NAMES = (
    "Adams", "Allen", "Anderson", "Bailey", "Baker", "Barnes", "Bell", "Bennett",
    "Brooks", "Brown", "Bryant", "Butler", "Campbell", "Carter", "Clark", "Coleman",
    "Collins", "Cook", "Cooper", "Cox", "Davis", "Diaz", "Edwards", "Evans",
    "Fisher", "Flores", "Foster", "Garcia", "Gomez", "Gonzalez", "Gray", "Green",
    "Griffin", "Hall", "Harris", "Hayes", "Henderson", "Hernandez", "Hill", "Howard",
    "Hughes", "Jackson", "James", "Jenkins", "Johnson", "Jones", "Kelly", "King",
    "Lee", "Lewis", "Long", "Lopez", "Martin", "Martinez", "Miller", "Mitchell",
    "Moore", "Morgan", "Morris", "Murphy", "Nelson", "Nguyen", "Parker", "Perez",
    "Perry", "Peterson", "Phillips", "Powell", "Price", "Ramirez", "Reed", "Reyes",
    "Richardson", "Rivera", "Roberts", "Robinson", "Rodriguez", "Rogers", "Ross",
    "Russell", "Sanchez", "Sanders", "Scott", "Simmons", "Smith", "Stewart", "Sullivan",
    "Taylor", "Thomas", "Thompson", "Torres", "Turner", "Walker", "Ward", "Watson",
    "White", "Williams", "Wilson", "Wood", "Wright", "Young",
)


def random_full_name() -> str:
    """Random first + last name (Title Case)."""
    return f"{secrets.choice(_FIRST_NAMES)} {secrets.choice(_LAST_NAMES)}"


def random_age(*, low: int = 19, high: int = 30) -> int:
    """Random age trong khoảng [low, high]."""
    return secrets.randbelow(high - low + 1) + low


def random_password(*, length: int = 12) -> str:
    """Random password 12 ký tự:
        - Bắt đầu bằng 1 chữ HOA.
        - Có chữ thường + số.
        - Kết thúc bằng @ hoặc # (ký tự ngẫu nhiên trong "@#").

    Format: [A-Z][a-z0-9]*8 + 1 chữ + 1 số + [@#]
    Tổng 12 ký tự.
    """
    if length < 4:
        raise ValueError("password length tối thiểu là 4")

    upper = secrets.choice(string.ascii_uppercase)
    end = secrets.choice("@#")

    # Phần giữa (length - 2) ký tự — đảm bảo có ít nhất 1 lower + 1 digit
    middle_len = length - 2
    if middle_len < 2:
        middle = secrets.choice(string.ascii_lowercase) + secrets.choice(string.digits)
    else:
        # Lấy 1 lower + 1 digit + (middle_len - 2) ký tự random từ alphanumeric
        chars = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
        ]
        pool = string.ascii_lowercase + string.digits
        chars.extend(secrets.choice(pool) for _ in range(middle_len - 2))
        # Shuffle phần middle để vị trí lower/digit không cố định
        random.shuffle(chars)
        middle = "".join(chars)

    return f"{upper}{middle}{end}"


def random_profile() -> dict:
    """Combo random: name + age + password + birthdate (compute từ age)."""
    age = random_age()
    name = random_full_name()
    password = random_password()
    today = datetime.utcnow()
    birth_year = today.year - age
    # Chọn ngày random trong năm để tránh trùng
    month = secrets.randbelow(12) + 1
    day = secrets.randbelow(28) + 1
    return {
        "name": name,
        "age": age,
        "password": password,
        "birthdate": f"{birth_year:04d}-{month:02d}-{day:02d}",
    }
