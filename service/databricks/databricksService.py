import json
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

DATABRICKS_KEY=os.environ.get("DATABRICKS_KEY")
DATABRICKS_URL=os.environ.get("DATABRICKS_URL")
WAREHOUSE_ID=os.environ.get("WAREHOUSE_ID")

w=WorkspaceClient(
    host=DATABRICKS_URL,
    token=DATABRICKS_KEY
)

#Upload to databricks
def dumpDataInDatabricks(path, content):
    try:
        w.files.upload(path, content, overwrite=True)
        return {"message": f"File uploaded to {path}"}
    except Exception as e:
        print(e)
        return { "message": "Internal Server Error", "success": False}

def generateDataBricksTool():
    return f"""
def retrieve_chunked_data(query_content: str):
    totalData = ""
    DATABRICKS_INSTANCE = "{DATABRICKS_URL}"
    TOKEN = "{DATABRICKS_KEY}"
    WAREHOUSE_ID = "{WAREHOUSE_ID}"

    headers = {{
        "Authorization": f"Bearer {{TOKEN}}",
        "Content-Type": "application/json"
    }}

    data = {{
        "statement": \"\"\"
            SELECT
                k.chunk_id,
                k.content,
                ai_similarity(queryContent, k.content) AS similarity
            FROM workspace.default.knowledge_base_pdf_chunks k
            ORDER BY similarity DESC
            LIMIT 3
        \"\"\",
        "warehouse_id": WAREHOUSE_ID
    }}

    # Submit SQL statement
    response = requests.post(
        f"{{DATABRICKS_INSTANCE}}/api/2.0/sql/statements/",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    statementObj = response.json()
    STATEMENT_ID = statementObj["statement_id"]

    # Poll until query finishes
    status_url = f"{{DATABRICKS_INSTANCE}}/api/2.0/sql/statements/{{STATEMENT_ID}}"

    while True:
        response = requests.get(status_url, headers=headers)
        result = response.json()
        state = result['status']['state']
        if state == "SUCCEEDED":
            return result
        else:
            time.sleep(2)

"""




