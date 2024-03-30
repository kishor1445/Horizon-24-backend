import cloudinary.uploader as CloudUploader
import cloudinary
import requests
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, status, Query
from bson import ObjectId
from app.config import db
from app.schema import Event, CreateRegisterEvent, RegisterEvent, PaymentStatus, PyObjectId
from app.utility.mail import send, event_reg_mail
from app.utility.security import is_valid_image


router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=List[Event])
async def get_events():
    data = await db.get_collection("events").find().to_list(None)
    return data


@router.post("/register", response_model=RegisterEvent)
async def register_event(data: CreateRegisterEvent):
    existing_data = await db.event_register.find_one(
        {"event_id": data.event_id, "reg_no": data.reg_no}
    )
    if existing_data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already registered for this event",
        )
    existing_data = await db.event_register.find_one(
        {"transaction_id": data.transaction_id}
    )
    if existing_data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This Transaction ID is already used",
        )
    existing_data = await db.event_register.find_one(
        {"screenshot_id": data.screenshot_id}
    )
    screenshot_url = cloudinary.CloudinaryImage(data.screenshot_id).build_url()
    with requests.get(screenshot_url) as req:
        if req.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This Screenshot ID doesn't exist",
            )
    if existing_data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This Screenshot ID is already used",
        )
    num_data = len(await db.event_register.find().to_list(None))
    event_data = await db.events.find_one({"_id": ObjectId(data.event_id)})
    TicketID = f"HRZ-{'N' if event_data['type'].startswith('non') else 'T'}-{str(num_data).zfill(5)}"
    if not event_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Event Does Not Exist"
        )
    if not event_data["seat"] + 1 <= event_data["max_seat"]:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Sold Out"
        )

    _data = data.model_dump()
    _data["status"] = PaymentStatus.PENDING.value
    _data["attended"] = False
    _data["ticket_id"] = TicketID
    if _data.get("team", None):
        if len(_data["team"]) > 3:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="There must be at most 4 members only in a team o.o",
            )
    await db.events.update_one(
        {"_id": event_data["_id"]}, {"$set": {"seat": event_data["seat"] + 1}}
    )
    _id = (await db.event_register.insert_one(_data)).inserted_id
    await send(
        email_ids=[data.email],
        subject=event_data["name"],
        html_body=event_reg_mail(event_data, _data),
    )
    event_reg_data = await db.event_register.find_one({"_id": _id})
    if event_reg_data:
        event_reg_data["screenshot_url"] = screenshot_url
    return event_reg_data


@router.get("/check_status_reg_no")
async def check_status_with_reg_no(reg_no: int):
    _data = []
    async for db_data in db.event_register.find({"reg_no": reg_no}):
        event_data = await db.events.find_one({"_id": ObjectId(db_data["event_id"])})
        _data.append({
            "event_name": event_data["name"],
            "status": db_data["status"],
            "transaction_id": db_data['transaction_id'],
            "fee": event_data["fee"]
        })
    return _data


@router.post("/payment_screenshot")
async def upload_payment_screenshot(screenshot: UploadFile):
    img = await screenshot.read()
    if not is_valid_image(screenshot.filename, img):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpg, jpeg and png files are allowed",
        )
    data = CloudUploader.upload(img)
    return {"id": data["public_id"]}

@router.get("/event_details", response_model=Event)
async def get_event_details(event_id: str):
    _data = await db.events.find_one({"_id": ObjectId(event_id)})
    _data["_id"] = PyObjectId(_data["_id"])
    return _data

@router.get("/ticket", response_model=RegisterEvent)
async def get_ticket_details(ticket_id: str):
    _data = await db.event_register.find_one({"ticket_id": ticket_id})
    print(_data)
    if _data:
        _data["screenshot_url"] = cloudinary.CloudinaryImage(_data["screenshot_id"]).build_url()
    return _data

@router.get("/check_event_status", response_model=list[RegisterEvent])
async def check_event_status(_id: str = Query(..., alias='id')):
    _data = await db.event_register.find({"_id": ObjectId(_id)}).to_list(None)
    if _data:
        for i in range(len(_data)):
            _data[i]["screenshot_url"] = cloudinary.CloudinaryImage(_data[i]["screenshot_id"]).build_url()
    return _data
