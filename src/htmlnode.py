class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props


    def to_html(self):
        raise NotImplementedError()


    def props_to_html(self):
        if self.props:
            out = ""
            for k, v in self.props.items():
                out += f" {k}=\"{v}\""
            return out
        else:
            return ''


    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, props=None):
        super().__init__(tag=tag, value=value, props=props)


    def to_html(self):
        return f"<{self.tag}{self.props_to_html()}>{self.value if self.value != None else ''}</{self.tag}>"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, children=children, props=props)


    def to_html(self):
        if not self.tag:
            raise ValueError("Parent nodes require tags")
        if not self.children:
            raise ValueError("Parent nodes must have associated children")
        inner = ''.join(list(map(lambda x: x.to_html(), self.children)))
        return f"<{self.tag}>{inner if inner != None else ''}</{self.tag}>"
