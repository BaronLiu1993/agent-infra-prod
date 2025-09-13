import json
from databricks.sdk import WorkspaceClient
import os
from dotenv import load_dotenv
import uuid
from databricks.sdk.service.workspace import ImportFormat
import base64

load_dotenv()

DATABRICKS_KEY=os.environ.get("DATABRICKS_KEY")
DATABRICKS_URL=os.environ.get("DATABRICKS_URL")

w=WorkspaceClient(
    host=DATABRICKS_URL,
    token=DATABRICKS_KEY
)

print(w.get_workspace_id())

#Dump Files into Databricks
def dumpDataInDatabricks(data):
    dataTag = uuid.uuid4()
    jsonStr = json.dumps(data)
    dbfsPath = f"/Volumes/workspace/default/htn_volume/{dataTag}.json"
    encoded_bytes = jsonStr.encode("utf-8")
    w.files.upload(dbfsPath, encoded_bytes, overwrite=True)
    return dbfsPath


def createNotebook():
    notebook_content = """
# This is a new notebook!
print("Hello from a programmatically created notebook.")
"""
    notebook_path = "/Users/baronliu1993@gmail.com/new_notebook_from_sdk"
    
    # 1. Encode the content string to bytes.
    content_bytes = notebook_content.encode('utf-8')
    
    # 2. Base64-encode the bytes.
    base64_bytes = base64.b64encode(content_bytes)
    
    # 3. Decode the Base64 bytes back to a string for the API call.
    base64_string = base64_bytes.decode('utf-8')
    
    # The 'format' must be SOURCE for raw code.
    try:
        w.workspace.import_(
            path=notebook_path,
            format=ImportFormat.AUTO,
            content=base64_string
        )
        print(f"Notebook created successfully at: {notebook_path}")
    except Exception as e:
        print(f"Failed to create notebook. Error: {e}")

# Call the function to create the notebook


sample_data = {
    "id": 1,
    "name": "Alice",
    "age": 30,
    "is_active": True,
    "scores": [95, 87, 92],
    "profile": {
        "department": "Engineering",
        "skills": ["Python", "SQL", "Databricks"]
    }
}

print(createNotebook())

