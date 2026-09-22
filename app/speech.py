from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class SpeechService:
    """Optional offline narration through the built-in Windows speech engine."""

    def __init__(self, script_path: Path) -> None:
        self._script_path = script_path
        self._powershell = shutil.which("powershell.exe") if os.name == "nt" else None
        self._process: subprocess.Popen[str] | None = None

    @property
    def available(self) -> bool:
        return self._powershell is not None and self._script_path.is_file()

    def speak(self, text: str) -> bool:
        if not self.available or not text.strip():
            return False
        self.stop()
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            self._process = subprocess.Popen(
                [
                    self._powershell,
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(self._script_path),
                    "-Rate",
                    "-1",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                creationflags=creation_flags,
            )
            assert self._process.stdin is not None
            self._process.stdin.write(text)
            self._process.stdin.close()
            return True
        except (OSError, ValueError):
            self._process = None
            return False

    def stop(self) -> None:
        if self._process is None:
            return
        if self._process.poll() is None:
            try:
                self._process.terminate()
            except OSError:
                pass
        self._process = None

