import unittest
from unittest import TestCase
from main import extract_title


class Tests(TestCase):
    def test_extract_title(self):
        test_func = extract_title
        md = """# Hello, world
This is my markdown
# This is another title

But that shouldn't have any effect"""
        self.assertEqual(
            test_func(md),
            "Hello, world"
        )


if __name__ == "__main__":
    unittest.main()
