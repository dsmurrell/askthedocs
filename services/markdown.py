import re

markdown_text = """
<br/>

<br/>

# Device code flow

❗ See note regarding implementation

## Description

Users should be prompted for a 6 digit "device code" after logging in. This is sent to the user by email. Once entered they should be logged in.

This device code is not required in the same session where they have registered, as they are required to access their email already to complete the registration.

On the server, the `validate_jwt()` now checks for a valid device cookie for all restriction decorators except where the device/login code entry is made. This ensures that the user is the old version of 'logged in' before entering their code. The new version of 'logged in' now includes a check for a valid device cookie on the FE.

## Implementation

This implementation uses a server org variable to "ring fence" the code login feature to the server running with an `org` of `bior`. Server checks for an environment variable (E.g. `org=bior`) at [various points in the auth flow](https://github.com/sanogenetics/sano/pull/6104/files#diff-4d8089ba84cb6336bb9681fbb6f7f2550ef641a586dfd21e7f408fd46d65ad8aR148). If not `bior` a valid device token is set in a `portal-device` cookie and therefore the user is not prompted for one. If `bior`, the user is required to have an existing  valid device token is set in a `portal-device` cookie or prompted to set one.

When we have implemented decent UI + UX (user comms) in the `/client` client, and the `/admin` client, this ring fence will be removed. We think a good time to do this will be after the 100 user send out for BioResource as we can receive some user feedback through this process.

### Local developement

To set the server env to bior for local developement use:

Linux/Mac

	Server:  `run/server bior`

	E2E Server: `run/server_e2e bior` 

Windows

	Server:  `run/server-win bior` 

	E2E Server: `run/server_e2e-win bior` 


"""


def parse_markdown(document, title="Heading 0"):
    # Regular expressions for detecting headings and content
    regex = re.compile(r"^(#+)\s(.*)$", re.MULTILINE)

    # Find the headings and their levels
    headings = regex.findall(document)

    # Initialize the root node
    root_node = {
        "title": title,
        "content": document.strip(),
        "length": len(document.strip()),
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

    def get_subtree_content(document, start_index, end_index):
        return document[start_index:end_index].strip()

    # Add nodes to the hierarchy
    for index, heading in enumerate(headings):
        level = len(heading[0])
        title = heading[1]

        # Find the content of the heading
        start_index = document.find(heading[0] + " " + title)
        if index + 1 < len(headings):
            end_index = document.find(
                "\n" + headings[index + 1][0] + " ", start_index + 1
            )
        else:
            end_index = len(document)

        content = get_subtree_content(document, start_index, end_index)

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


def update_content(node, breadcrumbs):
    if not node["children"]:
        node["breadcrumbs"] = breadcrumbs
        node["content"] = f"{node['breadcrumbs']}\n{node['content']}"
        node["length"] = len(node["content"])
        return node["content"]
    else:
        child_contents = "\n\n".join(
            update_content(child, breadcrumbs + " > " + node["title"])
            for child in node["children"]
        )
        node["content"] = f"{node['content']}\n\n{child_contents}"
        node["length"] = len(node["content"])
        return node["content"]


# Parse the document
document_node = parse_markdown(markdown_text)

# Update each child node with the full subtree text
for child_node in document_node["children"]:
    update_content(child_node, document_node["title"])

print(document_node)


# def parse_markdown(document, title="Document"):
#     # Regular expressions for detecting headings and content
#     regex = re.compile(r"^(#+)\s(.*)$", re.MULTILINE)

#     # Find the headings and their levels
#     headings = regex.findall(document)

#     # Initialize the root node
#     root_node = {
#         "title": title,
#         "content": document.strip(),
#         "length": len(document.strip()),
#         "level": 0,
#         "children": [],
#     }

#     # Function to add a node to the hierarchy
#     def add_node(parent, node):
#         if not parent["children"]:
#             parent["children"].append(node)
#         else:
#             last_child = parent["children"][-1]
#             if last_child["level"] < node["level"]:
#                 add_node(last_child, node)
#             else:
#                 parent["children"].append(node)

#     def get_subtree_content(document, start_index, end_index):
#         return document[start_index:end_index].strip()

#     # Add nodes to the hierarchy
#     for index, heading in enumerate(headings):
#         level = len(heading[0])
#         title = heading[1]

#         # Find the content of the heading
#         start_index = document.find(heading[0] + " " + title)
#         if index + 1 < len(headings):
#             end_index = document.find(
#                 "\n" + headings[index + 1][0] + " ", start_index + 1
#             )
#         else:
#             end_index = len(document)

#         content = get_subtree_content(document, start_index, end_index)

#         node = {
#             "title": title,
#             "content": content,
#             "length": len(content),
#             "level": level,
#             "children": [],
#         }

#         add_node(root_node, node)

#     return root_node


# def update_content(node):
#     if not node["children"]:
#         return node["content"]
#     else:
#         child_contents = "\n\n".join(
#             update_content(child) for child in node["children"]
#         )
#         node["content"] = f"{node['content']}\n\n{child_contents}"
#         node["length"] = len(node["content"])
#         return node["content"]


# # Parse the document
# document_node = parse_markdown(markdown_text)

# # Update each child node with the full subtree text
# for child_node in document_node["children"]:
#     update_content(child_node)

# print(document_node)


from helpers import pretty_print_dict

pretty_print_dict(document_node)
