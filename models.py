from sqlmodel import Field, Relationship, SQLModel


# Attendance
class Attendance(SQLModel, table=True):
    member_id: int | None = Field(foreign_key="member.member_id", primary_key=True)
    class_id: int | None = Field(foreign_key="class.class_id", primary_key=True)

# Member
class Member(SQLModel, table=True):
    member_id: int | None = Field(primary_key=True)
    name: str
    classes: list["Class"] = Relationship(back_populates="members", link_model=Attendance)

# Trainer
class Trainer(SQLModel, table=True):
    trainer_id: int | None = Field(primary_key=True)
    name: str
    specialty: str
    classes: list["Class"] = Relationship(back_populates="trainer")

# Class
class Class(SQLModel, table=True):
    class_id: int | None = Field(primary_key=True)
    name: str
    date: str
    duration: int
    trainer_id: int = Field(foreign_key="trainer.trainer_id")
    trainer: Trainer = Relationship(back_populates="classes")
    members: list[Member] = Relationship(back_populates="classes", link_model=Attendance)