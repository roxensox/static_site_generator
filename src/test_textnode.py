import unittest

from textnode import TextNode, TextType
import splitter_funcs
from splitter_funcs import text_node_to_html_node, split_nodes_delimiter
import split_block as sb
from block import BlockType


class TestTextNode(unittest.TestCase):
    maxDiff = None

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
        node = TextNode("`this` is a `test`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], '`', TextType.CODE)
        node_list = [
            TextNode("this", TextType.CODE),
            TextNode(" is a ", TextType.TEXT),
            TextNode("test", TextType.CODE)
        ]
        self.assertEqual(new_nodes, node_list)

        node2 = TextNode("`this is also a test", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node, node2], '`', TextType.CODE)
        node_list.extend([TextNode("`this is also a test", TextType.TEXT)])
        self.assertEqual(new_nodes, node_list)

        node3 = TextNode("this is a __real__ test", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node3], "__", TextType.ITALIC)
        node_list = [TextNode("this is a ", TextType.TEXT), TextNode("real", TextType.ITALIC), TextNode(" test", TextType.TEXT)]
        self.assertEqual(new_nodes, node_list)

        node4 = TextNode("__this__ __is__ __a__ __test__ __too__", TextType.TEXT)
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
        self.assertEqual(splitter_funcs.extract_markdown_links("this is a test"), [])
        self.assertEqual(splitter_funcs.extract_markdown_links("[anchor text](link url)"), [("anchor text", "link url"),])
        self.assertEqual(splitter_funcs.extract_markdown_links("[anchor text1](link1) [anchor text2](link2)"), [("anchor text1", "link1"), ("anchor text2", "link2")])


    def test_image_extraction(self):
        self.assertEqual(splitter_funcs.extract_markdown_images("no images here"), [])
        self.assertEqual(splitter_funcs.extract_markdown_images("![this is anchor text](here's an image link)"), [("this is anchor text", "here's an image link")])
        self.assertEqual(splitter_funcs.extract_markdown_images("![at1](lnk1) ![at2](lnk2)"), [("at1", "lnk1"), ("at2", "lnk2")])
        self.assertEqual(splitter_funcs.extract_markdown_images("[anchor](link)"), [])


    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = splitter_funcs.split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )


    def test_split_links(self):
        node = TextNode(
            "This is text with an [internet link](https://i.imgur.com/zjjcJKZ.png) and another [internet link 2](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = splitter_funcs.split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("internet link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "internet link 2", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = splitter_funcs.split_nodes_link([node])
        self.assertEqual([TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )], new_nodes)

        nodes = [
            TextNode("This has an ![image](https://i.imgur.com/lollmfao.jpg) link and a [regular](https://www.google.com) link",
            TextType.TEXT),
            TextNode("This one also has a [link](https://lol.com)",
            TextType.TEXT)
        ]
        new_nodes = splitter_funcs.split_nodes_link(nodes)
        self.assertEqual(
            [
                TextNode("This has an ![image](https://i.imgur.com/lollmfao.jpg) link and a ",
                TextType.TEXT),
                TextNode("regular",
                TextType.LINK,
                "https://www.google.com"),
                TextNode(" link",
                TextType.TEXT),
                TextNode("This one also has a ",
                TextType.TEXT),
                TextNode("link",
                TextType.LINK,
                "https://lol.com")
            ],
            new_nodes
        )

    def test_text_to_nodes(self):
        test_func = splitter_funcs.text_to_text_nodes
        test = test_func("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        should_be = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(test, should_be)

        test = test_func("**here _is_**_ some _**bold** text so I can be _really_ sure that it works.")
        should_be = [
            TextNode("here _is_", TextType.BOLD),
            TextNode(" some ", TextType.ITALIC),
            TextNode("bold", TextType.BOLD),
            TextNode(" text so I can be ", TextType.TEXT),
            TextNode("really", TextType.ITALIC),
            TextNode(" sure that it works.", TextType.TEXT)
        ]
        self.assertEqual(test, should_be)

    def test_markdown_to_blocks(self):
        test_func = sb.markdown_to_blocks
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = test_func(md)
        self.assertEqual(
        blocks,
        [
            "This is **bolded** paragraph",
            "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            "- This is a list\n- with items",
        ],
        )

    def test_block_to_block_type(self):
        m2b = sb.markdown_to_blocks
        b2bt = sb.block_to_block_type
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        self.assertEqual([b2bt(i) for i in m2b(md)],
                         [
                         BlockType.PARAGRAPH,
                         BlockType.PARAGRAPH,
                         BlockType.UNORDERED_LIST
                         ])

        md = """
```This is a code block```

- This
- Is
- An
- Unordered
- List

1. And
2. This
1234. One
4. Is ordered

> This is a 
>Quote block

# HEADING HERE

#######This one is normal though

## Heading

#Normal

# """
        self.assertEqual([b2bt(i) for i in m2b(md)],
                         [
                         BlockType.CODE,
                         BlockType.UNORDERED_LIST,
                         BlockType.ORDERED_LIST,
                         BlockType.QUOTE,
                         BlockType.HEADING,
                         BlockType.PARAGRAPH,
                         BlockType.HEADING,
                         BlockType.PARAGRAPH,
                         BlockType.PARAGRAPH
                         ])

    def test_m2html(self):
        test_func = sb.markdown_to_html_node
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = test_func(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff</code></pre></div>",
        )

        md = "## Hello, **world**"
        node = test_func(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h2>Hello, <b>world</b></h2></div>"
        )

        md = """- LubyDoo
- Luna
- The Lubinator
- The Lube Father
"""
        node = test_func(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>LubyDoo</li><li>Luna</li><li>The Lubinator</li><li>The Lube Father</li></ul></div>"
        )

        md = """1. LubyDoo
2. Luna
3. The Lubinator
500. The Lube Father
"""
        node = test_func(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>LubyDoo</li><li>Luna</li><li>The Lubinator</li><li>The Lube Father</li></ol></div>"
        )
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = test_func(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )


if __name__ == "__main__":
    unittest.main()
