"""Tests for CUSIP validators"""
import unittest
from src.utils.validators import validate_cusip, format_cusip


class TestValidators(unittest.TestCase):
    """Test CUSIP validation"""

    def test_valid_cusip(self):
        """Test valid CUSIP"""
        is_valid, msg = validate_cusip("912828Z29")
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_invalid_length(self):
        """Test invalid CUSIP length"""
        is_valid, msg = validate_cusip("12345")
        self.assertFalse(is_valid)
        self.assertIn("9 characters", msg)

    def test_invalid_characters(self):
        """Test invalid characters"""
        is_valid, msg = validate_cusip("912828Z2!")
        self.assertFalse(is_valid)
        self.assertIn("alphanumeric", msg)

    def test_invalid_format(self):
        """Test invalid format (last char must be digit)"""
        is_valid, msg = validate_cusip("912828Z2A")
        self.assertFalse(is_valid)

    def test_empty_cusip(self):
        """Test empty CUSIP"""
        is_valid, msg = validate_cusip("")
        self.assertFalse(is_valid)
        self.assertIn("empty", msg)

    def test_format_cusip(self):
        """Test CUSIP formatting"""
        formatted = format_cusip("  912828z29  ")
        self.assertEqual(formatted, "912828Z29")


if __name__ == "__main__":
    unittest.main()
