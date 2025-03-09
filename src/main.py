from textnode import TextNode, TextType


def main():
    test = TextNode("hello, world", TextType.BOLD)
    print(test)

if __name__ == "__main__":
    main()
