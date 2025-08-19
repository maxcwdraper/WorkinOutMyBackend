from pydantic import BaseModel


class CreateMemberRequest(BaseModel):
    name: str

class CreateTrainerRequest(BaseModel):
    name: str
    specialty: str