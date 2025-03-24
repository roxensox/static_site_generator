import unittest
from unittest import TestCase
from main import extract_title, generate_page
import os
from config import PROJECT, PUBLIC, STATIC


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

        md = """Hello, world
# This is the title
### This isn't
"""
        self.assertEqual(
            test_func(md),
            "This is the title"
        )

        try:
            test_func("""
This is a title
""")
            error = None
        except:
            error = 1

        self.assertEqual(
            error,
            1
        )

    def test_generate_page(self):
        from_path = os.path.join(STATIC, "test1.md")
        dest_path = os.path.join(PUBLIC, "test1.html")
        template_path = os.path.join(PROJECT, "template.html")

        generate_page(from_path, template_path, dest_path)



if __name__ == "__main__":
    unittest.main()
