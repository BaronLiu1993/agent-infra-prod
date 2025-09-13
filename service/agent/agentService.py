from dotenv import load_dotenv
import pystache
from typing import List, Dict, Any
from google import genai
from google.genai import types
import os
from pydantic import BaseModel
import json

load_dotenv()

GEMINI_API_KEY= os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

"""
Starting here the service layer is being generated and compiled for the agentic workflows
1. Starting with Generating Imports and Configuration For Memories and Logging
"""


class Prompt(BaseModel):
    prompt: str
    strategies: List[str]

def generateGraphNodeImports():
    return """
from celery import Celery
from openai import OpenAI
from google import genai
from dotenv import load_dotenv 
import base64
from google.genai import types
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Dict, Any
from datetime import datetime
import uuid

import requests
import json

GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")
"""

def databaseSetup():
    return """
engine = create_engine("postgresql://demo:demo123@localhost:5432/agentinfradb")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import text
from pgvector.sqlalchemy import Vector 
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Memory(Base):
    __tablename__ = "memory"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    input = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    output = Column(String, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Logs(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    data = Column(JSONB, nullable=False)
    log_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
"""

#ADD LOGGING INTO THESE FUNCTIONS IF TIME PERMITS
#Add Insert Memories Into Vector DB
def generateInsertEmbeddingCode():
    return """
def generateEmbeddings(text: str):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


def insertEmbedding(input: str, output: str, prompt: str, node_id: int):
    try:
        with SessionLocal() as session:
            embedding = generateEmbeddings(input)
            
            memoryRow = Memory(
                input=input,
                output=output,
                prompt=prompt,
                embedding=embedding
            )
            
            loggingRow = Logs(
                name="embedding",
                node_id=node_id,
                data={"input": input, "output": output, "prompt": prompt},
                log_type="embedding",
                status="success"
            )
            
            session.add(loggingRow)
            session.add(memoryRow)
            
            session.commit()
            
            session.refresh(loggingRow)
            session.refresh(memoryRow)
            
            return {"success": True, "message": "Successfully Inserted"}
    except Exception as e:
        print(f"Error inserting embedding: {e}")
        return {"success": False, "message": "Internal Server Error"}

"""

#ADD LOGGING INTO THESE FUNCTIONS IF TIME PERMITS
def generateCallMemoryTool():
    return """
def retrieve_memories(thought: str, number_of_memories: int):
    \"\"\"
    Retrieve the vector embedding for a stored memory.

    This function fetches the vector embedding associated and data on
    it such as the input, output and prompt of the LLM
    \"\"\"
    query_vector = generateEmbeddings(thought)
    sql = text(\"\"\"
        SELECT *, embedding <=> :query_vector AS similarity
        FROM memory
        ORDER BY similarity
        LIMIT :number_of_memories
    \"\"\")
    with SessionLocal() as session:
        result = session.execute(sql, {
            "query_vector": query_vector,
            "number_of_memories": number_of_memories
        })
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
"""

#Do Two Example One For Healthcare and One for Finance
def generateLoggingWrappers():
    return """
def insertLoggingData(name, nodeId, data: Dict[str, Any], logType: str):
    try:
        with SessionLocal() as session:
            loggingRow = Logs(name=name, node_id=nodeId, data=data, log_type=logType, status="success")
            session.add(loggingRow)
            session.commit()
            session.refresh(loggingRow)
            return { "success": True, "message": "Successully Inserted"}
    except Exception as e:
        with SessionLocal() as session:
            loggingRow = Logs(name=name, node_id=nodeId, data=data, log_type=logType, status="failed")
            session.add(loggingRow)
            session.commit()
            session.refresh(loggingRow)   
        return { "success": False, "message": "Internal Server Error" }
"""


def generateQueueCode():
    return """
brokerLayer = "amqp://guest:guest@localhost:5672//"
cacheLayer = "redis://localhost:6379/0"

celery = Celery("LLMQueue", broker=brokerLayer, backend=cacheLayer)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
"""

"""
FINISH IF I HAVE TIME
def generateGetMLCode(workflowId, nodeId, description, url, authToken, parameters, searchParams=None, databricksURL):
    try:   
        
    except Exception as e:
        raise Exception(e)

"""

def generateGoogleToolCalling():
    return """
google_search_tool = types.Tool(
    google_search=types.GoogleSearch()
)
"""

#Not Supported By 2.0-Flash Maybe By Others
def generateCodeExecution():
    return """
code_execution_tool = types.Tool(
    code_execution=types.ToolCodeExecution()
)
"""

"""
Together with the other APIs
"""

#Generate API Calling Code 
def generatePostAPINodeCode(workflowId, nodeId, description, url, authToken, body, parameters, searchParams):
    rendered_url = pystache.render(url, searchParams or {})
    rendered_parameters = ", ".join(
    [f'{p["name"]}: {p["type"]}' if isinstance(p, dict) else str(p) for p in parameters]
)
    return f"""
def {nodeId}({rendered_parameters}):
    {description}
    try:
        response = requests.post(
            "{rendered_url}",
            headers={{
                "Authorization": "Bearer {authToken}",
                "Content-Type": "application/json"
            }},
            json={body}
        )
        
        data = {{
            "id": id,
            "workflow_id": "{workflowId}",
            "endpoint": "{rendered_url}",
            "executed": timestamp,
            "environment": "production",
            "status_code": response.status_code,
            "headers": response.headers,
        }}
        insertLoggingData("API", "{nodeId}", data, "POST METHOD")
        return response.json()
    except Exception as e:
        data = {{
            "id": id,
            "workflow_id": "{workflowId}",
            "endpoint": "{rendered_url}",
            "executed": timestamp,
            "environment": "production",
            "status_code": response.status_code,
            "headers": response.headers,
        }}
        insertLoggingData("API", "{nodeId}", data, "GET METHOD")
        raise Exception(e)
"""

def generateDeleteAPINodeCode(workflowId, nodeId, description, url, authToken, parameters, searchParams=None):
    rendered_url = pystache.render(url, searchParams or {})
    rendered_parameters = ", ".join(
        [p["name"] if isinstance(p, dict) else str(p) for p in parameters]
    )
    return f"""
def {nodeId}({rendered_parameters}):
    {description}
    id = str(uuid.uuid4())
    timestamp = datetime.now()
    try:
        response = requests.delete(
            "{rendered_url}",
            headers={{"Authorization": "Bearer {authToken}"}}
        )
        
        data = {{
            "id": id,
            "workflow_id": {workflowId},
            "endpoint": {rendered_url},
            "executed": timestamp,
            "environment": "production",
            "status_code": response.status_code,
            "headers": response.headers,
        }}
        insertLoggingData("API", "{nodeId}", data, "DELETE METHOD")
        return response.json()
    except Exception as e:
        data = {{
            "id": id,
            "endpoint": {rendered_url},
            "executed": timestamp,
            "environment": "production",
            "status_code": response.status_code,
            "headers": response.headers,
        }}
        insertLoggingData("API", "{nodeId}", data, "DELETE", "SUCCESS")
        raise Exception(e)
"""

def generateGetAPINodeCode(workflowId, nodeId, description, url, authToken, parameters, searchParams=None):
    rendered_url = pystache.render(url, searchParams or {})
    rendered_parameters = ", ".join(
    [p["name"] if isinstance(p, dict) else str(p) for p in parameters]
)
    return f"""

def {nodeId}({rendered_parameters}):
    {description}

    id = str(uuid.uuid4())
    timestamp = datetime.now()
    try:
        response = requests.get(
            "{rendered_url}",
            headers={{"Authorization": "Bearer {authToken}"}}
        )
        response.raise_for_status()
        data = {{
            "id": id,
            "workflow_id": "{workflowId}",
            "endpoint": "{rendered_url}",
            "executed": timestamp,
            "environment": "production",
            "status_code": response.status_code,
            "headers": response.headers,
        }}
        insertLoggingData("API", "{nodeId}", data, "GET METHOD")
        return response.json()
    except Exception as e:
        data = {{
                "id": id,
                "workflow_id": "{workflowId}",
                "endpoint": "{rendered_url}",
                "executed": timestamp,
                "environment": "production",
                "status_code": response.status_code,
                "headers": response.headers,
            }}
        insertLoggingData("API", "{nodeId}", data, "GET METHOD")
        raise Exception(e)
"""

#For Something Else Right Now
def generateSchema(rawInputSchema: dict, rawOutputSchema: dict):
    input_str = "\n".join(f"    {k}: {v}" for k, v in rawInputSchema.items())
    output_str = "\n".join(f"    {k}: {v}" for k, v in rawOutputSchema.items())
    return f"""
class inputSchema(BaseModel):
{input_str}

class outputSchema(BaseModel):
{output_str}
"""

#Function list will be a name of all the functions ["function1", "function2"] and it is the name of the declaration
def generateDecisionTextGeminiNodeCode(workflowId:str, nodeId: str, systemPrompt: str, description: str, model: str, apiKey: str, prompt: str, schema: str, functionList: List):
    executeTools = """
        for candidate in response.candidates:
            for part in candidate.content.parts:
                tool_call = getattr(part, "function_call", None)
                if not tool_call or not hasattr(tool_call, "name"):
                    continue 
"""
    functionListDeclarations ="[" + ", ".join(functionList) + "]"
    for function in functionList:
        executeTools += f"""
                if part.function_call.name == {function}:
                    result = {function}(**tool_call.args)
                    function_response_part = types.Part.from_function_response(
                        name=part.function_call.name,
                        response={{ "result": result }}
                    )
                    contents.append(candidate)
                    contents.append(types.Content(role="user", parts=[function_response_part]))
"""
    return f"""
client = genai.Client(api_key=GEMINI_API_KEY)

config = types.GenerateContentConfig(
    tools={functionListDeclarations},
    system_instruction="{systemPrompt}"
)

contents = [
    types.Content(
        role="user", parts=[types.Part(text="{prompt}")]
    )
]

def {nodeId}(modelInput = ""):
    timestamp = datetime.now()
    try:
        response = client.models.generate_content(
            model="{model}",
            contents=contents,
            config=config
        )
        
        {executeTools}
        data = {{
                "workflow_id": "{workflowId}",
                "model": "{model}",
                "tokens_in": response.usage_metadata.prompt_token_count,
                "token_out": response.usage_metadata.candidates_token_count,
                "token_total": response.usage_metadata.total_token_count,
                "executed": timestamp,
                "environment": "production",
                "status_code": 200,
                "prompt": "{systemPrompt + prompt}",
                "input": modelInput,
                "output": response.text,
                "response_size": len(response.text.encode("utf-8"))
            }}
        insertLoggingData("LLM", "{nodeId}", data, "LLM Method")
        insertEmbedding(modelInput, response.text, "{systemPrompt + prompt}") 
        finalResponse = client.models.generate_content(
            model="{model}",
            config=config,
            contents=contents
        )
        return finalResponse.text
    except Exception as e:
        raise Exception(e)
"""

#Controller Will Send Data in the form of ["name1", "name2"]

"""
Starting here the controller layer is being compiled
"""

def generateControllerConfiguration(serviceImports: List[Dict[str, Any]]):
    configuration = f"""
from fastapi import FastAPI
from pydantic import BaseModel
"""
    for service in serviceImports:
        configuration += f"""
from service.{service} import {service}
"""
    configuration += f"""
app = FastAPI()
"""
    return configuration

#In the format
"""
    [{name1, variable1, parameter1}, {name2, variable2, paramter2}]
    parameter2 should be variable1

"""

"""
to work it needs initialInput in first in the first selection
  "functions": [
            {"variable": "variable", "name": "name", "parameter": "initialInput"},
            {"variable": "variable2", "name": "name2", "parameter": "variable"}
        ]
"""

def connectAgents(functions: List[Dict[str, Any]]):
    functionDefinition = "def executeAgents(initialInput: str):\n"
    
    for f in functions:
        functionDefinition += f"    {f['variable']} = {f['name']}({f['parameter']})\n"
    
    functionDefinition += "    return {" + ", ".join(f"'{f['variable']}': {f['variable']}" for f in functions) + "}\n"

    return functionDefinition

        

#Have it be in main layer
def generateControllerMethod():

    return f"""
class InputSchema(BaseModel):
    initialInput: str

@app.post("/execute-agent-workflow")
def executeAgentWorkflow(request: InputSchema):
    print(request)
    try:
        response = executeAgents(request.initialInput)
        return response
    except Exception as e:
        print(e)
        raise Exception(e)

@app.get("/health")
def health():
    try:
        return {{ "message": "Hi HackTheNorth! The container is healthy!"}}
    except Exception as e:
        raise Exception(e)
"""

#Improve the prompt give it documentation feed it and then learn feed it gemini documentation
def promptComposer(prompt: str):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            response_mime_type= "application/json",
            response_schema=Prompt,
            system_instruction=(
                f"You are a professional prompt engineer. "
                f""
            ), 
        ),
        contents=[types.Content(parts=[types.Part(text=prompt)])] 
    )
    json_data = response.text
    parsed = json.loads(json_data)  
    return parsed
