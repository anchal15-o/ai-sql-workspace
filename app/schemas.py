from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str


class DBConnectionRequest(BaseModel):
    connection_uri: str


class SQLExecuteRequest(BaseModel):
    connection_uri: str
    sql: str


class PromptRunRequest(BaseModel):
    connection_uri: str
    prompt: str


class OllamaSettings(BaseModel):
    model: str = "llama3:8b"