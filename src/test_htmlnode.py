import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestTextNode(unittest.TestCase):
    def test_repr(self):
        node = HTMLNode()
        assert(node.__repr__() == "HTMLNode(None, None, None, None)")


    def test_props_to_html(self):
        node = HTMLNode(props={
        "href": "https://www.google.com",
        "target": "_blank",
        })
        assert(node.props_to_html() == ' href="https://www.google.com" target="_blank"')


    def test_empty_node(self):
        node = HTMLNode()
        assert(node.props_to_html() == '')


    def test_leaf_node(self):
        l_node = LeafNode(tag="p", value="bungo", props={"href": "https://www.google.com/"})
        self.assertEqual(l_node.props_to_html(), ' href="https://www.google.com/"')


    def test_leaf_node_to_html(self):
        l_node = LeafNode(tag="p", value="bungo", props={"href": "https://www.google.com/"})
        self.assertEqual(l_node.to_html(), '<p href="https://www.google.com/">bungo</p>')


    def test_leaf_node_print(self):
        l_node = LeafNode()
        self.assertEqual(l_node.__repr__(), 'HTMLNode(None, None, None, None)')


    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")


    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

if __name__ == "__main__":
    unittest.main()
