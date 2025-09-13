from fastapi import FastAPI
from controllers import infraRouter, githubRouter, agentRouter
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(infraRouter.router, prefix="/infra", tags=["infra"])
app.include_router(githubRouter.router, prefix="/github", tags=["github"])
app.include_router(agentRouter.router, prefix="/agent", tags=["agent"])