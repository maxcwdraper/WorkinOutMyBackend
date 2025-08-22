from pydantic import BaseModel


class AddMemberToClassRequest(BaseModel):
    member_id: int

class AddTrainerToClassRequest(BaseModel):
    trainer_id: int

class CreateMemberRequest(BaseModel):
    name: str

class CreateTrainerRequest(BaseModel):
    name: str
    specialty: str

class CreateClassRequest(BaseModel):
    name: str
    date: str
    duration: int
    trainer_id: int

class GetClassResponse(BaseModel):
    name: str
    date: str
    duration: int
    trainer: str
    members: list[str]

class GetMemberResponse(BaseModel):
    name: str
    classes: list[str]

class GetTrainerResponse(BaseModel):
    name: str
    specialty: str
    classes: list[str]

class UpdateMemberRequest(BaseModel):
    name: str | None = None
    active: bool | None = None

class UpdateTrainerRequest(BaseModel):
    name: str | None = None
    specialty: str | None = None

class UpdateClassRequest(BaseModel):
    name: str | None = None
    date: str | None = None
    duration: int | None = None