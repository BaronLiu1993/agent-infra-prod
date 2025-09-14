from fastapi import APIRouter
from service.infra.infraService import createDroplet, retrieveDropletData

from pydantic import BaseModel

router = APIRouter()

class GenerateDropletRequest(BaseModel):
    name: str
    repoName: str
    userName: str
    postgresUser: str
    postgresPassword: str

class DropletDataRequest(BaseModel):
    dropletId: str

"""
@router.post("/create-object-storage")
def createObjectStorage():
    try:
        response = 
"""

@router.post("/create-droplet")
def createVM(DropletDetails: GenerateDropletRequest):
    try:
        response = createDroplet(DropletDetails.name, DropletDetails.userName, DropletDetails.repoName, DropletDetails.postgresUser, DropletDetails.postgresPassword)
        return response
    except Exception as e:
        raise Exception(e)

@router.get("/get-droplet")
def getDroplet(dropletId: str):
    try:
        response = retrieveDropletData(dropletId)
        return response
    except Exception as e:
        raise Exception(e)
