import json
from databricks.sdk import WorkspaceClient
import os
from dotenv import load_dotenv
import uuid

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


"""
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
"""



