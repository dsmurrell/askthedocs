import re
import sys
import textwrap

from alchemy.models import Document, Node
from helpers import compute_hash


def parse_markdown(markdown, title="Heading 0"):
    # Regular expressions for detecting headings and content
    regex = re.compile(r"^(#+)\s(.*)$", re.MULTILINE)

    # Find the headings and their levels
    headings = regex.findall(markdown)

    # Initialize the root node
    root_node = {
        "title": title,
        "content": markdown.strip(),
        "length": len(markdown.strip()),
        "level": 0,
        "children": [],
        "breadcrumbs": title,
    }

    # Function to add a node to the hierarchy
    def add_node(parent, node):
        if not parent["children"]:
            parent["children"].append(node)
        else:
            last_child = parent["children"][-1]
            if last_child["level"] < node["level"]:
                add_node(last_child, node)
            else:
                parent["children"].append(node)

    def get_subtree_content(markdown, start_index, end_index):
        return markdown[start_index:end_index].strip()

    # Add nodes to the hierarchy
    for index, heading in enumerate(headings):
        level = len(heading[0])
        title = heading[1]

        # Find the content of the heading
        start_index = markdown.find(heading[0] + " " + title)
        if index + 1 < len(headings):
            end_index = markdown.find(
                "\n" + headings[index + 1][0] + " ", start_index + 1
            )
        else:
            end_index = len(markdown)

        content = get_subtree_content(markdown, start_index, end_index)

        node = {
            "title": title,
            "content": content,
            "length": len(content),
            "level": level,
            "children": [],
            "breadcrumbs": "",
        }

        add_node(root_node, node)

    return root_node


# Maximum length of content in a node
MAX_CONTENT_LENGTH = 1000
OVERLAP_LENGTH = 100


def split_long_content(content, level, breadcrumbs, overlap=OVERLAP_LENGTH):
    wrapper = textwrap.TextWrapper(
        width=MAX_CONTENT_LENGTH - overlap, break_long_words=False
    )
    wrapped_content = wrapper.wrap(content)

    chunks = []
    start = 0
    end = MAX_CONTENT_LENGTH

    for i, chunk in enumerate(wrapped_content):
        if i == 0:
            chunks.append(chunk)
            end = start + len(chunk)
        else:
            end = start + len(chunk) + overlap
            chunks.append(content[start:end])

        start = end - overlap

    nodes = []
    for idx, chunk in enumerate(chunks):
        # Don't include the last breadcrumb for the first part
        content_breadcrumbs = (
            ">".join(breadcrumbs.split(">"))
            if idx > 0
            else ">".join(breadcrumbs.split(">")[:-1])
        )
        content = f"{content_breadcrumbs}\n{chunk}"
        node = {
            "title": f"Part {idx + 1}",
            "content": content,
            "length": len(chunk) + len(content_breadcrumbs),
            "level": level,
            "children": [],
            "breadcrumbs": breadcrumbs + f" > Part {idx + 1}",
        }
        nodes.append(node)

    return nodes


def add_breadcrumbs(node, breadcrumbs):
    node["breadcrumbs"] = breadcrumbs
    node["content"] = f"{node['breadcrumbs']}\n{node['content']}"
    node["length"] = len(node["content"])


def update_content(node, breadcrumbs):
    breadcrumbs_addition = (" > " + node["title"]) if node["level"] > 0 else ""

    if not node["children"]:
        if node["length"] > MAX_CONTENT_LENGTH:
            node["children"] = split_long_content(
                node["content"], node["level"] + 1, breadcrumbs + breadcrumbs_addition
            )

        add_breadcrumbs(node, breadcrumbs)

        return node["content"]
    else:
        child_contents = "\n\n".join(
            update_content(child, breadcrumbs + breadcrumbs_addition)
            for child in node["children"]
        )
        node["content"] = f"{node['content']}\n\n{child_contents}"
        node["length"] = len(node["content"])
        return node["content"]


def add_node_to_db(session, node, document_id, parent_id=None):
    node_hash = compute_hash(node["content"])

    # Check if the node with the same hash already exists in the database
    db_node = session.query(Node).filter_by(hash=node_hash).first()

    if not db_node:
        db_node = Node(
            title=node["title"],
            text=node["content"],
            hash=node_hash,
            text_length=node["length"],
            depth_level=node["level"],
            parent_id=parent_id,
            document_id=document_id,
        )
        session.add(db_node)
        session.flush()  # To get the generated id for the new node

        for child in node.get("children", []):
            add_node_to_db(session, child, document_id, db_node.id)

        [compute_hash(child["content"]) for child in node.get("children", [])]

        # Remove any old nodes that have the same parent but are not in the new tree
        session.query(Node).filter(
            Node.parent_id == db_node.id,
            ~Node.hash.in_(
                [compute_hash(child["content"]) for child in node.get("children", [])]
            ),
        ).delete(synchronize_session="fetch")


def update_nodes(session):
    for document in session.query(Document).all():
        # Parse the document
        document_node = parse_markdown(document.text_no_html, document.title)

        # Update each child node with the full subtree text
        for child_node in document_node["children"]:
            update_content(child_node, document_node["title"])

        add_node_to_db(session, document_node, document.id)
        session.commit()
        sys.stdout.write(".")
        sys.stdout.flush()
