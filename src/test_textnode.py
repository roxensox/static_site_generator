import unittest

from textnode import TextNode, TextType
from main import text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_neq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is another text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_neq_url(self):
        node = TextNode("This is a text node", TextType.BOLD, url="https://www.google.com")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_text_node_to_html_node(self):
        node = TextNode("This is a text node", TextType.BOLD, url="https://www.google.com")
        html_version = text_node_to_html_node(node)
        self.assertEqual(html_version.tag, 'b')
        self.assertEqual(html_version.value, "This is a text node")
        self.assertEqual(html_version.to_html(), "<b>This is a text node</b>")

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_image(self):
        node = TextNode("This is another text node", TextType.IMAGE, "https://www.google.com/")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.props, {"alt":"This is another text node", "src":"https://www.google.com/"})
        self.assertEqual(html_node.to_html(), '<img src="https://www.google.com/" alt="This is another text node"></img>')

if __name__ == "__main__":
    unittest.main()
