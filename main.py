from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import desc, Session, select
from sqlalchemy import func

from database import get_db
from models import Attendance, Class, Member, Trainer
from schemas import AddMemberToClassRequest, AddTrainerToClassRequest, CreateClassRequest, CreateMemberRequest, CreateTrainerRequest, GetClassResponse, GetMemberResponse, GetTrainerResponse, UpdateClassRequest, UpdateMemberRequest, UpdateTrainerRequest


app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


### GET ###

@router.get("/members", tags=["members"])
async def get_members(db: Session = Depends(get_db)) -> list[GetMemberResponse]:
    members: list[Member] = db.exec(select(Member)).all()
    member_responses: list[GetMemberResponse] = []
    for member in members:
        class_names: list[str] = []
        for one_class in member.classes:
            class_names.append(one_class.name)
        member_response: GetMemberResponse = GetMemberResponse(name=member.name, classes=class_names)
        member_responses.append(member_response)
    return member_responses

@router.get("/members/active", tags=["members"])
async def get_active_members(db: Session = Depends(get_db)) -> list[GetMemberResponse]:
    members: list[Member] = db.exec(select(Member).where(Member.active==True)).all()
    member_responses: list[GetMemberResponse] = []
    for member in members:
        class_names: list[str] = []
        for one_class in member.classes:
            class_names.append(one_class.name)
        member_response: GetMemberResponse = GetMemberResponse(name=member.name, classes=class_names)
        member_responses.append(member_response)
    return member_responses

@router.get("/members/{member_id}", tags=["members"])
async def get_member(member_id: int, db: Session = Depends(get_db)) -> GetMemberResponse:
    member: Member | None = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found.")
    class_names: list[str] = []
    for one_class in member.classes:
        class_names.append(one_class.name)
    member_response: GetMemberResponse = GetMemberResponse(name=member.name, classes=class_names)
    return member_response

@router.get("/trainers", tags=["trainers"])
async def get_trainers(db: Session = Depends(get_db)) -> list[GetTrainerResponse]:
    trainers: list[Trainer] = db.exec(select(Trainer)).all()
    trainer_responses: list[GetTrainerResponse] = []
    for trainer in trainers:
        class_names: list[str] = []
        for one_class in trainer.classes:
            class_names.append(one_class.name)
        trainer_response: GetTrainerResponse = GetTrainerResponse(name=trainer.name, specialty=trainer.specialty, classes=class_names)
        trainer_responses.append(trainer_response)
    return trainer_responses

@router.get("/trainers/{trainer_id}", tags=["trainers"])
async def get_trainer(trainer_id: int, db: Session = Depends(get_db)) -> GetTrainerResponse:
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    if trainer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID {trainer_id} not found.")
    class_names: list[str] = []
    for one_class in trainer.classes:
        class_names.append(one_class.name)
    trainer_response: GetTrainerResponse = GetTrainerResponse(name=trainer.name, specialty=trainer.specialty, classes=class_names)
    return trainer_response

@router.get("/classes", tags=["classes"])
async def get_classes(db: Session = Depends(get_db)) -> list[GetClassResponse]:
    classes: list[Class] = db.exec(select(Class)).all()
    class_responses: list[GetClassResponse] = []
    for one_class in classes:
        member_names: list[str] = []
        for member in one_class.members:
            member_names.append(member.name)
        class_response: GetClassResponse = GetClassResponse(name=one_class.name, date=one_class.date, duration=one_class.duration, trainer=one_class.trainer.name, members=member_names)
        class_responses.append(class_response)
    return class_responses

@router.get("/classes/{class_id}", tags=["classes"])
async def get_class(class_id: int, db: Session = Depends(get_db)) -> GetClassResponse:
    one_class: Class | None = db.get(Class, class_id)
    if one_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    member_names: list[str] = []
    for member in one_class.members:
        member_names.append(member.name)
    class_response: GetClassResponse = GetClassResponse(name=one_class.name, date=one_class.date, duration=one_class.duration, trainer=one_class.trainer.name, members=member_names)
    return class_response

@router.get("/classes/{class_id}/members", tags=["classes"])
async def get_class_member_list(class_id: int, db: Session = Depends(get_db)) -> list[str]:
    searching_class: Class | None = db.get(Class, class_id)
    if searching_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    member_names: list[str] = []
    for member in searching_class.members:
        member_names.append(member.name)
    return member_names

@router.get("/classes/{class_id}/memberslength", tags=["attendance"])
async def get_class_member_count(class_id: int, db: Session = Depends(get_db)) -> int:
    searching_class: Class | None = db.get(Class, class_id)
    if searching_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    return len(searching_class.members)

@router.get("/trainers/{trainer_id}/classes/{class_id}/members", tags=["attendance"])
async def get_trainer_class_member_count(class_id: int, trainer_id: int, db: Session = Depends(get_db)) -> int:
    trainer_class: Class | None = db.get(Class, class_id)
    if trainer_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    if trainer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID {trainer_id} not found.")
    if trainer.trainer_id != trainer_class.trainer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer not teaching this class.")
    return len(trainer_class.members)

@router.get("/classes/date", tags=["classes"])
async def get_most_popular_day(db: Session = Depends(get_db)) -> str:
    statement = select(
        Class.date,
        func.count(Class.class_id).label("count")
    ).group_by(Class.date).order_by(desc("count")).limit(1)
    most_popular_day = db.exec(statement).first()
    if most_popular_day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No classes found.")
    return most_popular_day


### POST ###

@router.post("/members", status_code=status.HTTP_201_CREATED, tags=["members"])
async def create_member(create_member_request: CreateMemberRequest, db: Session = Depends(get_db)) -> int:
    member: Member = Member(**create_member_request.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member.member_id

@router.post("/trainers", status_code=status.HTTP_201_CREATED, tags=["trainers"])
async def create_trainer(create_trainer_request: CreateTrainerRequest, db: Session = Depends(get_db)) -> int:
    trainer: Trainer = Trainer(**create_trainer_request.model_dump())
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return trainer.trainer_id

@router.post("/classes", status_code=status.HTTP_201_CREATED, tags=["classes"])
async def create_class(create_class_request: CreateClassRequest, db: Session = Depends(get_db)) -> int:
    created_class: Class = Class(**create_class_request.model_dump())
    db.add(created_class)
    db.commit()
    db.refresh(created_class)
    return created_class.class_id

@router.post("/classes/{class_id}/members", status_code=status.HTTP_201_CREATED, tags=["classes"])
async def add_member_to_class(class_id: int, request: AddMemberToClassRequest, db: Session = Depends(get_db)) -> None:
    member: Member | None = db.get(Member, request.member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {request.member_id} not found.")
    adding_class: Class | None = db.get(Class, class_id)
    if adding_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    if member in adding_class.members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member already in class.")
    adding_class.members.append(member)
    db.commit()

@router.post("/classes/{class_id}/trainer", status_code=status.HTTP_201_CREATED, tags=["classes"])
async def add_trainer_to_class(class_id: int, request: AddTrainerToClassRequest, db: Session = Depends(get_db)) -> None:
    trainer: Trainer | None = db.get(Trainer, request.trainer_id)
    if trainer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID {request.trainer_id} does not exist.")
    adding_class: Class | None = db.get(Class, class_id)
    if adding_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    if trainer in adding_class.trainer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trainer already teaches this class.")
    adding_class.trainer = trainer
    adding_class.trainer_id = trainer.trainer_id
    db.commit()


### PATCH ###

@router.patch("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["members"])
async def update_member(member_id: int, update_member_request: UpdateMemberRequest, db: Session = Depends(get_db)) -> None:
    member: Member | None = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found.")
    for field, value in update_member_request.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    db.commit()

@router.patch("/trainers/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["trainers"])
async def update_trainer(trainer_id: int, update_trainer_request: UpdateTrainerRequest, db: Session = Depends(get_db)) -> None:
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    if trainer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID {trainer_id} not found.")
    for field, value in update_trainer_request.model_dump(exclude_unset=True).items():
        setattr(trainer, field, value)
    db.commit()

@router.patch("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["classes"])
async def update_class(class_id: int, update_class_request: UpdateClassRequest, db: Session = Depends(get_db)) -> None:
    updated_class: Class | None = db.get(Class, class_id)
    if updated_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    for field, value in update_class_request.model_dump(exclude_unset=True).items():
        setattr(updated_class, field, value)
    db.commit()


### DELETE ###

@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["members"])
async def delete_member(member_id: int, db: Session = Depends(get_db)) -> None:
    member: Member | None = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found.")
    db.delete(member)
    db.commit()

@router.delete("/trainers/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["trainers"])
async def delete_trainer(trainer_id: int, db: Session = Depends(get_db)) -> None:
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    if trainer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID {trainer_id} not found.")
    db.delete(trainer)
    db.commit()

@router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["classes"])
async def delete_class(class_id: int, db: Session = Depends(get_db)) -> None:
    deleting_class: Class | None = db.get(Class, class_id)
    if deleting_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    db.delete(deleting_class)
    db.commit()

@router.delete("/classes/{class_id}/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["classes"])
async def delete_class_trainer(class_id: int, trainer_id: int, db: Session = Depends(get_db)) -> None:
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    if trainer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID {trainer_id} not found.")
    deleting_class: Class | None = db.get(Class, class_id)
    if deleting_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID {class_id} not found.")
    if trainer_id != deleting_class.trainer_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID {trainer_id} not in class with ID {class_id}.")
    db.delete(deleting_class.trainer)
    db.delete(deleting_class.trainer_id)
    db.commit()

app.include_router(router)