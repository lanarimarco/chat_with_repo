from langchain_core.tools import BaseTool

from chat_with_repo.assistant import State

class AbstractTool(BaseTool):
    state: State