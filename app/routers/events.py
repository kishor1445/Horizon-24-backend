import cloudinary.uploader as CloudUploader
import cloudinary
import requests
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, status
from bson import ObjectId
from app.config import db
from app.schema import Event, CreateRegisterEvent, RegisterEvent, PaymentStatus
from app.utility.mail import send, event_reg_mail
from app.utility.security import is_valid_image


router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=List[Event])
async def get_events():
    return await db.get_collection("events").find().to_list(None)


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
    event_data = await db.events.find_one({"_id": ObjectId(data.event_id)})
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
    return await db.event_register.find_one({"_id": _id})


@router.get("/check_status")
async def check_status(reg_no: int):
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
