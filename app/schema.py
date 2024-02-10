from datetime import datetime
from enum import Enum
from typing import Annotated, List
from pydantic import BeforeValidator, BaseModel, EmailStr, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class EventType(Enum):
    TECHNICAL = "technical"
    NON_TECHNICAL = "non_technical"


class PaymentStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"


class PyID(BaseModel):
    id: PyObjectId = Field(alias="_id")


class Team(BaseModel):
    reg_no: int
    name: str
    department: str
    section: str
    year: int


class EventBase(BaseModel):
    name: str
    type: EventType
    seat: int
    max_seat: int
    description: str
    start: datetime
    end: datetime
    fee: float
    venue: str
    image_url: str
    whatsapp_group_link: str


class CreateEvent(EventBase):
    ...


class UpdateEvent(BaseModel):
    name: str | None = None
    type: EventType | None = None
    seat: int | None = None
    max_seat: int | None = None
    description: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    fee: float | None = None
    venue: str | None = None
    image_url: str | None = None
    whatsapp_group_link: str | None = None


class Event(EventBase):
    id: PyObjectId | None = Field(alias="_id", default=None)


class RegisterEventBase(BaseModel):
    name: str
    reg_no: int
    team: List[Team] | None = None
    transaction_id: str
    screenshot_id: str
    department: str
    section: str
    year: int
    email: EmailStr
    event_id: PyObjectId


class CreateRegisterEvent(RegisterEventBase):
    ...


class RegisterEvent(RegisterEventBase):
    id: PyObjectId | None = Field(alias="_id", default=None)
    status: PaymentStatus = PaymentStatus.PENDING
    attended: bool


class VerifyPayment(BaseModel):
    reg_no: int
    event_id: str
    status: PaymentStatus
