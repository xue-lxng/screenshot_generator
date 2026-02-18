from pydantic import BaseModel


class ScreenshotTaskResponse(BaseModel):
    status: str
    task_id: str