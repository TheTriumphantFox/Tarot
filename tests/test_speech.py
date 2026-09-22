from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.speech import SpeechService


class _InputCapture(io.StringIO):
    def close(self) -> None:
        self.was_closed = True


class _FakeProcess:
    def __init__(self) -> None:
        self.stdin = _InputCapture()
        self.terminated = False

    def poll(self):
        return None

    def terminate(self) -> None:
        self.terminated = True


class SpeechServiceTests(unittest.TestCase):
    def test_speech_is_local_opt_in_process_with_stdin_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "speak.ps1"
            script.write_text("# test", encoding="utf-8")
            fake = _FakeProcess()
            with (
                patch("app.speech.shutil.which", return_value=r"C:\\Windows\\powershell.exe"),
                patch("app.speech.subprocess.Popen", return_value=fake) as popen,
            ):
                service = SpeechService(script)
                self.assertTrue(service.available)
                self.assertTrue(service.speak("The Star. Upright."))
                self.assertEqual("The Star. Upright.", fake.stdin.getvalue())
                args = popen.call_args.args[0]
                self.assertIn("-NoProfile", args)
                self.assertIn(str(script), args)
                service.stop()
                self.assertTrue(fake.terminated)


if __name__ == "__main__":
    unittest.main()
