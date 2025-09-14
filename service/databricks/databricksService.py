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

def dumpDataInDatabricks(path, content):
    try:
        w.files.upload(path, content, overwrite=True)
        return {"message": f"File uploaded to {path}"}
    except Exception as e:
        print(e)
        return { "message": "Internal Server Error", "success": False}




