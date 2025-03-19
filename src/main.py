from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re


def main():
    test = TextNode("hello, world", TextType.BOLD)
    print(test)


if __name__ == "__main__":
    main()
