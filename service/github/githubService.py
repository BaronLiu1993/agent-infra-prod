from github import Github
from github import Auth
from fastapi.responses import PlainTextResponse
import base64
import uuid
import os
import base64

GithubAccess = os.environ.get("GITHUB_ACCESS")
auth = Auth.Token(GithubAccess)

def setKey(repoName: str, privateKey, keyName: str):
    try:
        g = Github(auth=auth)
        user = g.get_user()
        repo = user.get_repo(repoName)

        response = repo.create_secret(
            secret_name=keyName,
            unencrypted_value=privateKey,
            secret_type="actions"
        )
        print(response)
        return {"message": "Sucessfully Added Key", "success": True}
    except Exception as e:
        print(e)
        return { "message": "Internal Server Error", "success": False}


def createRepository(name: str):
    try:
        g=Github(auth=auth)
        user = g.get_user()
        repoCode = uuid.uuid4()
        repo = user.create_repo(f"{name}-${repoCode}", private = False)
        print(repo)
        return { "message": "Successfully Created Repo", "success": True, "data": repo.full_name}
    except Exception as e:
        print(e)
        return { "message": "Internal Server Error", "success": False}

def listFiles(path: str, repo_name: str):
    try:   
        g = Github(auth= auth)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path=path)
        items = []
        for item in contents:
            items.append({
            "name": item.name,
            "path": item.path,
            "type": item.type 
        })
        return {"files": items, "message": "Sucessfully Retrieved Files", "success": True}
    except Exception as e:
        return {"message": "Internal Server Error", "success": False}     

def getFileContent(path: str, repo_name: str):
    try:
        g = Github(auth= auth)
        repo = g.get_repo(repo_name)
        file = repo.get_contents(path)
        content = base64.b64decode(file.content).decode()
        fileContent = PlainTextResponse(content)
        return {"fileContent": fileContent, "message": "Sucessfully Retrieved Files", "success": True}
    except Exception as e:
        return {"message": "Internal Server Error", "success": False}     
    
def createFile(code: str, commitMessage: str, path: str, repoName: str, githubUser: str):
    try:
        g = Github(auth= auth)
        repo = g.get_repo(f"{githubUser}/{repoName}")
        repo.create_file(
            path=path,
            message=commitMessage,
            content=code
        )
        return {"message": "Created Successfully", "success": True}     
    except Exception as e:
        print(e)
        return {"message": "Internal Server Error", "success": False}     

def updateFile(newCode: str, commitMessage: str, path: str, repoName: str, githubUser: str):
    try:
        print(githubUser)
        print(repoName)
        g = Github(auth=auth)
        repo = g.get_repo(f"{githubUser}/{repoName}")
        file = repo.get_contents(path)
        print(file)
        response=repo.update_file(
            path=path,
            message=commitMessage,
            content = newCode,
            sha=file.sha
        )
        return {"message": "Pushed Successfully", "success": True}     
    except Exception as e:
        print(e)
        return {"message": "Internal Server Error", "success": False}     

def configureCICD(repoName: str):
    try:   
        g = Github(auth=auth)
        print(repoName)
        user = g.get_user()
        repo = user.get_repo(repoName)
        print(repo)
        workflow_path = ".github/workflows/ci.yml"
        workflow_content = f"""name: CI/CD
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.DEPLOY_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.DROPLET_IP }} >> ~/.ssh/known_hosts

      - name: Deploy
        run: |
          ssh root@${{ secrets.DROPLET_IP }} << 'EOF'
            cd /opt/app
            git reset --hard
            git pull origin main
            pip3 install -r requirements.txt
            systemctl restart fastapi
          EOF
"""

        create = repo.create_file(workflow_path, "Successfully Updated CI workflow", workflow_content)
        print(create)
        return {"message": "Workflow created successfully", "success": True}
    except Exception as e:
        print(e)
        return { "message": "Internal Server Error", "success": False}

def createRequirementsFile(requirements: list[str]):
    requirementFile = ""
    for requirement in requirements:
        requirementFile += requirement
    return requirementFile



