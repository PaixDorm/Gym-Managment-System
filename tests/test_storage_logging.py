import unittest
import tempfile

from pathlib import Path
from unittest.mock import patch

from src.storage.file_manager import (
    read_file,
    write_file,
    append_file,
    update_file
)

from src.logging.activity_logger import save_log


class TestFileManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.path = str(
            Path(self.temp_dir.name) / "test.txt"
        )

    def test_write_and_read(self):
        write_file(self.path, "Hello")
        self.assertEqual(read_file(self.path), "Hello")

    def test_append(self):
        write_file(self.path, "Hello")
        append_file(self.path, " World")

        self.assertEqual(
            read_file(self.path),
            "Hello World"
        )

    def test_update(self):
        write_file(self.path, "old text")

        update_file(
            self.path,
            "old",
            "new"
        )

        self.assertEqual(
            read_file(self.path),
            "new text"
        )

    def test_overwrite(self):
        write_file(self.path, "first")
        write_file(self.path, "second")

        self.assertEqual(
            read_file(self.path),
            "second"
        )

    def test_persian_text(self):
        write_file(self.path, "سلام باشگاه")

        self.assertEqual(
            read_file(self.path),
            "سلام باشگاه"
        )


class TestActivityLogger(unittest.TestCase):

    @patch("src.logging.activity_logger.append_file")
    def test_save_log(self, mock_append):
        save_log(
            "test_action",
            "member",
            "test_user",
            True
        )

        mock_append.assert_called_once()

        path, content = mock_append.call_args.args

        self.assertIn("activity_logs.txt", path)
        self.assertIn("test_action", content)
        self.assertIn("member", content)
        self.assertIn("test_user", content)


if __name__ == "__main__":
    unittest.main()