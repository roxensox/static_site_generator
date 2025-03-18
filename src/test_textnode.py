import unittest

from textnode import TextNode, TextType
import main
from main import text_node_to_html_node, split_nodes_delimiter


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

    def test_node_splitter(self):
        node = TextNode("`this` is a `test`", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], '`', TextType.CODE)
        node_list = [TextNode("this", TextType.CODE), TextNode(" is a ", TextType.TEXT), TextNode("test", TextType.CODE)]
        self.assertEqual(new_nodes, node_list)

        node2 = TextNode("`this is also a test", TextType.CODE)
        new_nodes = split_nodes_delimiter([node, node2], '`', TextType.CODE)
        node_list.extend([TextNode("`this is also a test", TextType.TEXT)])
        self.assertEqual(new_nodes, node_list)

        node3 = TextNode("this is a __real__ test", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node3], "__", TextType.ITALIC)
        node_list = [TextNode("this is a ", TextType.TEXT), TextNode("real", TextType.ITALIC), TextNode(" test", TextType.TEXT)]
        self.assertEqual(new_nodes, node_list)

        node4 = TextNode("__this__ __is__ __a__ __test__ __too__", TextType.ITALIC)
        new_nodes = split_nodes_delimiter([node4], "__", TextType.ITALIC)
        node_list = [
            TextNode("this", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("is", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("a", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("test", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("too", TextType.ITALIC),
        ]
        self.assertEqual(new_nodes, node_list)


    def test_link_extraction(self):
        self.assertEqual(main.extract_markdown_links("this is a test"), [])
        self.assertEqual(main.extract_markdown_links("[anchor text](link url)"), [("anchor text", "link url"),])
        self.assertEqual(main.extract_markdown_links("[anchor text1](link1) [anchor text2](link2)"), [("anchor text1", "link1"), ("anchor text2", "link2")])


    def test_image_extraction(self):
        self.assertEqual(main.extract_markdown_images("no images here"), [])
        self.assertEqual(main.extract_markdown_images("![this is anchor text](here's an image link)"), [("this is anchor text", "here's an image link")])
        self.assertEqual(main.extract_markdown_images("![at1](lnk1) ![at2](lnk2)"), [("at1", "lnk1"), ("at2", "lnk2")])
        self.assertEqual(main.extract_markdown_images("[anchor](link)"), [])



if __name__ == "__main__":
    unittest.main()
