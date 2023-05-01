# import sys
# from pathlib import Path

# from notion_client import Client

# sys.path.append(str(Path(__file__).resolve().parent.parent))

# from config import config

# notion = Client(auth=config["notion_key"])

# # Query the database to get all its records
# results = notion.databases.query(
#     **{
#         "database_id": "3dc559e11aef494ea0319429bed74220",
#         "filter": {"property": "Status", "select": {"equals": "Published"}},
#         "sorts": [{"property": "Type", "direction": "ascending"}],
#     },
# )
# count = 0

# # Loop through the records and extract the URL from the "Document" property of each record
# for record in results["results"]:
#     # Get the "Document" property of the record
#     document_property = record.get("properties").get("Document")
#     try:
#         doc_url = document_property["title"][0]["text"]["link"]["url"]
#     except TypeError:
#         doc_url = None
#     except IndexError:
#         doc_url = None
#     if doc_url:
#         count += 1


# print(count)
