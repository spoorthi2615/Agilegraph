from pydantic import BaseModel, Field, ConfigDict
from typing import List

def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

class TopbarBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

class SearchResult(TopbarBaseModel):
    id: str
    title: str
    type: str  # 'asset', 'scan', 'report'
    subtitle: str
    url: str

class Notification(TopbarBaseModel):
    id: str
    title: str
    message: str
    time: str
    read: bool
    type: str # 'alert', 'info', 'success'

class Workspace(TopbarBaseModel):
    id: str
    name: str
    environment: str # 'PROD', 'STAGING', 'DEV'
    is_active: bool
