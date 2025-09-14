from fastapi import APIRouter, HTTPException, File, UploadFile
from service.agent.agentService import (
    generateGraphNodeImports, 
    databaseSetup, 
    generateInsertEmbeddingCode, 
    generateCallMemoryTool,
    generateQueueCode,
    generateLoggingWrappers,
    generateGetAPINodeCode,
    generatePostAPINodeCode,
    generateDeleteAPINodeCode,
    generateDecisionTextGeminiNodeCode,
    generateControllerConfiguration,
    generateControllerMethod, 
    connectAgents,
    generateCodeExecution,
    generateGoogleToolCalling,
    promptComposer, 
    generateSchema,
    generateVideoGeminiNodeCode,
    generateImageControllerMethod,
    generateImageGeminiNodeCode
)
from service.databricks.databricksService import (
    dumpDataInDatabricks,
    generateDataBricksTool
)
from service.documentation.documentationService import generateDocumentation
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid


router = APIRouter()

class GenerateServiceRequest(BaseModel):
    NodeConfiguration: List[Dict[str, Any]]

class GenerateDocumentationRequest(BaseModel):
    code: str
    documentationLanguage: str
    codingLanguage: str

#['name1', 'name2']
#[{variable, name, parameter}]

class GenerateMainRequest(BaseModel):
    routers: List[str]
    functions: List[Dict[str, Any]]
    modality: bool
# The controller will orchestrate
"""
Example Input 

"""

#One Id will represent one agent, multi agent
#Always create an agent first and then add tools so it will be the first will be added last
@router.post("/generate-service-layer")
def generateServiceLayer(request: GenerateServiceRequest):
    """
    Generates a complete Python service layer script based on a node configuration.
    """
    try:
        agentWorkflowScript = ""
        # Add setup code once at the beginning
        agentWorkflowScript += generateGraphNodeImports()
        agentWorkflowScript += databaseSetup()
        agentWorkflowScript += generateInsertEmbeddingCode()
        agentWorkflowScript += generateCallMemoryTool()
        agentWorkflowScript += generateQueueCode()
        agentWorkflowScript += generateLoggingWrappers()
        agentWorkflowScript += generateCodeExecution()
        agentWorkflowScript += generateGoogleToolCalling()
        agentWorkflowScript += generateDataBricksTool()

        # Iterate through each node configuration and generate its code
        for node in request.NodeConfiguration:
            node_type = node.get("type")

            if node_type == "GET":
                agentWorkflowScript += generateGetAPINodeCode(
                    workflowId=node.get("workflowId"),
                    nodeId=node.get("nodeId"),
                    description=node.get("description", ""),
                    parameters=node.get("parameters", []),
                    url=node.get("url"),
                    authToken=node.get("authToken"),
                    searchParams=node.get("searchParams")
                )
            elif node_type == "POST":
                agentWorkflowScript += generatePostAPINodeCode(
                    workflowId=node.get("workflowId"),
                    nodeId=node.get("nodeId"),
                    description=node.get("description", ""),
                    url=node.get("url"),
                    authToken=node.get("authToken"),
                    body=node.get("body", {}),
                    searchParams=node.get("searchParams"),
                    parameters=node.get("parameters", [])
                )
            elif node_type == "DELETE":
                agentWorkflowScript += generateDeleteAPINodeCode(
                    workflowId=node.get("workflowId"),
                    nodeId=node.get("nodeId"),
                    description=node.get("description", ""),
                    url=node.get("url"),
                    authToken=node.get("authToken"),
                    searchParams=node.get("searchParams")
                )
            elif node_type == "DecisionText":
                schema_code = generateSchema(node.get("inputSchema", {}), node.get("outputSchema", {}))
                agentWorkflowScript += generateDecisionTextGeminiNodeCode(
                    workflowId=node.get("workflowId"),
                    nodeId=node.get("nodeId"),
                    systemPrompt=node.get("systemPrompt", ""),
                    description=node.get("description", ""),
                    model=node.get("model", "models/gemini-1.5-flash"),
                    apiKey=node.get("apiKey"),
                    prompt=node.get("prompt", ""),
                    schema=schema_code,
                    functionList=node.get("functionList", []),
                )
            elif node_type == "DecisionVideo":
                agentWorkflowScript += generateVideoGeminiNodeCode(
                    workflowId=node.get("workflowId"),
                    nodeId=node.get("nodeId"),
                    prompt=node.get("prompt", ""),
                )
            elif node_type == "DecisionImage":
                agentWorkflowScript += generateImageGeminiNodeCode(
                    workflowId=node.get("workflowId"),
                    nodeId=node.get("nodeId"),
                    prompt=node.get("prompt", ""),
                )
        return agentWorkflowScript
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
#You can create many service layers
    
@router.post("/generate-main-layer")
def generateMainLayer(request: GenerateMainRequest):
    try:
        controllerLayer = ""
        controllerLayer += generateControllerConfiguration(request.routers)
        controllerLayer += connectAgents(request.functions)
        if request.modality:
            controllerLayer += generateControllerMethod()
        else:
            controllerLayer += generateImageControllerMethod()
        
        return controllerLayer
    except Exception as e:
        print(e)
        raise Exception(e)
    
@router.post("/generate-documentation")
def generateTechnicalDocumentation(documentationConfiguration: GenerateDocumentationRequest):
    try:
        documentation = generateDocumentation(documentationConfiguration.code, documentationConfiguration.documentationLanguage, documentationConfiguration.codingLanguage)
        return documentation
    except Exception as e:
        raise Exception(e)
    
@router.post("/upload/")
async def uploadDatabricks(file: UploadFile = File(...)):
    try:
        content = await file.read()
        # Preserve the original filename and extension
        dbfsPath = f"/Volumes/workspace/default/htn_volume/{file.filename}"
        response = dumpDataInDatabricks(dbfsPath, content)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    