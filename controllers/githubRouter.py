from pydantic import BaseModel
from fastapi import APIRouter
from service.github.githubService import createRepository, createFile, configureCICD, setKey, updateFile

router = APIRouter()

class GenerateRepoRequest(BaseModel):
    name: str

class CreateRepoFileRequest(BaseModel):
    code: str
    commitMessage: str
    path: str
    repoName: str
    githubUser: str

class SetKeysRequest(BaseModel):
    repo: str
    keyValue: str
    keyName: str

class ConfigureCICDRepoRequest(BaseModel):
    repoName: str

class UpdateFileRequest(BaseModel):
    newCode: str
    commitMessage: str 
    path: str 
    repoName: str
    githubUser: str

@router.post("/update-file")
def updateRepoFile(updateDetails: UpdateFileRequest):
    try:
        response = updateFile(updateDetails.newCode, updateDetails.commitMessage, updateDetails.path, updateDetails.repoName, updateDetails.githubUser)
        return response
    except Exception as e:
        raise Exception(e)

@router.post("/set-key")
def setSSHKeys(keyDetails: SetKeysRequest):
    try:
        response = setKey(keyDetails.repo, keyDetails.keyValue, keyDetails.keyName)
        return response
    except Exception as e:
        raise Exception(e)

@router.post("/configure-ci-cd")
def buildCICDPipeline(pipelineDetails: ConfigureCICDRepoRequest):
    try:
        response = configureCICD(pipelineDetails.repoName)
        return response
    except Exception as e:
        raise Exception(e)


@router.post("/create-repo")
def generateRepo(RepoDetails: GenerateRepoRequest):
    print(RepoDetails)
    try:
        response = createRepository(RepoDetails.name)
        return response
    except Exception as e:
        raise Exception(e)

@router.post("/create-file")
def createFileInRepo(FileDetails: CreateRepoFileRequest):
    try:
        response = createFile(FileDetails.code, FileDetails.commitMessage, FileDetails.path, FileDetails.repoName, FileDetails.githubUser)
        return response
    except Exception as e:
        raise Exception(e)

@router.get("/get-repo")
def getRepo():
    pass