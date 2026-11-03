import re

SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",
    r"gh[pousr]_[A-Za-z0-9]{36,}",
    r"github_pat_\w{20,}",
    r"AIza[\w-]{35}",
    r"sk-[A-Za-z0-9_-]{20,}",
    r"xox[baprs]-[\w-]{10,}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----",
]

ASSIGNED_SECRET = r"""(?i:[\w-]*(?:password|passwd|secret|api_?key|token)[\w-]*["']?\s*[:=]\s*["'][^"'\s]{8,}["'])"""

RISKY_COMMANDS = [
    r"\b(curl|wget|nc|ncat|ssh|scp)\b",
    r"git\s+push",
    r"\$\{\{",
    r"GITHUB_TOKEN",
    r"/dev/tcp",
    r"base64\s+(-d|--decode)",
    r"\beval\b",
]

HIDE_REGEX = re.compile("|".join(SECRET_PATTERNS + [ASSIGNED_SECRET]))


def hide_secrets(text: str, secrets: dict | None = None):
    def hide(match):
        if secrets is None:
            return "[HIDDEN_SECRET]"
        for name, value in secrets.items():
            if value == match.group():
                return name
        name = f"[SECRET_{len(secrets) + 1}]"
        secrets[name] = match.group()
        return name

    return HIDE_REGEX.sub(hide, text)


def restore_secrets(text: str, secrets: dict):
    for name, value in secrets.items():
        text = text.replace(name, value)
    return text


def find_problems(changes: dict, originals: dict, test_command: str):
    problems = []
    for path, code in changes.items():
        old_code = originals.get(path, "")
        for pattern in SECRET_PATTERNS:
            for match in re.finditer(pattern, code):
                if match.group() not in old_code:
                    problems.append(f"{path} has a new secret")

    for pattern in RISKY_COMMANDS:
        if re.search(pattern, test_command):
            problems.append("the test command is not allowed")

    return sorted(set(problems))
