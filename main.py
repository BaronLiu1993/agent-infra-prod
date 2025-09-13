from fastapi import FastAPI
from controllers import infraRouter, githubRouter, agentRouter

app = FastAPI()
app.include_router(infraRouter.router, prefix="/infra", tags=["infra"])
app.include_router(githubRouter.router, prefix="/github", tags=["github"])
app.include_router(agentRouter.router, prefix="/agent", tags=["agent"])