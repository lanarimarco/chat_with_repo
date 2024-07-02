from typing import Type
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from chat_with_repo.model import Repo, State



class SelectGitHubRepoSchema(BaseModel):
    repo: Repo = Field(..., description="The name of the GitHub repository.")

class SelectGitHubRepoTool(BaseTool):
    state: State
    args_schema: Type[BaseModel] = SelectGitHubRepoSchema
    name: str = "select_github_repo"
    description = "A tool that selects a GitHub repository."

    def _run(self, repo: Repo):
        self.state.repo = repo
        return f"{repo.owner}/{repo.value} has been selected. Remember the user that he can change the repository any time and that since now he is able to ask any questions as specifed in system message"
    
    