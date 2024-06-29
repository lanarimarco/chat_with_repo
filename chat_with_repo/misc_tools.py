from typing import Callable, Type
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from enum import Enum

from chat_with_repo.model import State

class Repo(Enum):
    jariko = "jariko"
    kokos_sdk_java_rpgle = "kokos-sdk-java-rpgle"
    webup_project = "webup-project"
    webup_js = "webup.js"

class SelectGitHubRepoSchema(BaseModel):
    repo: Repo = Field(..., description="The name of the GitHub repository.")

class SelectGitHubRepoTool(BaseTool):
    state: State
    args_schema: Type[BaseModel] = SelectGitHubRepoSchema
    name: str = "select_github_repo"
    description = "A tool that selects a GitHub repository."

    def _run(self, repo: Repo):
        self.state.repo = repo.value
        return f"{repo} has been selected. Remember the user that he can change the repository any time and that since now he is able to ask any questions as specifed in system message"
    
    