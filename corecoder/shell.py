"""Shell routing: POSIX commands need a POSIX shell.

On macOS/Linux `shell=True` already means /bin/sh. On Windows it means
cmd.exe, where pwd, ls, cat, sleep and friends do not exist. Every shell
spawn in CoreCoder goes through here so Windows gets Git Bash instead.
"""

import os
import shutil
import subprocess
from functools import lru_cache


@lru_cache(maxsize=1)
def _git_bash() -> str | None:
    """Locate Git Bash on Windows; None elsewhere or when absent.

    System32\\bash.exe is WSL (a different filesystem and environment, not
    the Git installation the user's commands target), so it is never picked.
    """
    if os.name != "nt":
        return None
    candidate = os.path.join(
        os.environ.get("ProgramFiles", r"C:\Program Files"), "Git", "bin", "bash.exe"
    )
    if os.path.isfile(candidate):
        return candidate
    git = shutil.which("git")
    if git:
        derived = os.path.join(os.path.dirname(os.path.dirname(git)), "bin", "bash.exe")
        if os.path.isfile(derived):
            return derived
    return None


def run_shell(command: str, check: bool = False, **kwargs) -> subprocess.CompletedProcess:
    """Run one POSIX command string, via Git Bash on Windows when present.

    The list form bypasses cmd.exe entirely; without Git Bash we fall back
    to the platform default (cmd.exe on Windows, /bin/sh elsewhere).
    """
    bash = _git_bash()
    if bash is not None:
        return subprocess.run([bash, "-c", command], shell=False, check=check, **kwargs)
    return subprocess.run(command, shell=True, check=check, **kwargs)
