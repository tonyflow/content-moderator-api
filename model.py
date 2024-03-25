from pydantic import BaseModel


class ClassificationRequest(BaseModel):
    """
    Request body for the classify method
    """
    text: str
