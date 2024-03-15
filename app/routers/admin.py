import os
import cloudinary
from fastapi import APIRouter, Query, status, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from bson import ObjectId
from bson.errors import InvalidId
from app.schema import (
    CreateEvent,
    UpdateEvent,
    Event,
    RegisterEvent,
    RegisterEventWithoutScreenshotUrl,
    VerifyPayment,
    PyID,
)
from app.config import db
from app.oauth2 import get_admin, create_access_token
from app.utility.qr import create_qr
from app.utility.mail import send, payment_verified_mail


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login")
def login_member(data: OAuth2PasswordRequestForm = Depends()):
    if not data.password == os.environ["ADMIN_PASSWORD"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )
    access_token = create_access_token({"reg_no": data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/events", status_code=status.HTTP_201_CREATED, response_model=PyID)
async def create_event(data: CreateEvent, admin_reg_no: int = Depends(get_admin)):
    _data = data.model_dump()
    _data["type"] = _data["type"].value
    data_id = (await db.events.insert_one(_data)).inserted_id
    return {"_id": data_id}


@router.patch("/events", response_model=Event)
async def update_event(
    data: UpdateEvent, _id=Query(alias="id"), admin_reg_no: int = Depends(get_admin)
):
    _id = ObjectId(_id)
    _data = data.model_dump()
    _data = {k: v for k, v in _data.items() if v is not None}
    if _data.get("type", None):
        _data["type"] = _data["type"].value
    await db.events.update_one({"_id": _id}, {"$set": _data})
    _data = await db.events.find_one({"_id": _id})
    return _data


@router.delete("/events", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_event(_id=Query(alias="id"), admin_reg_no: int = Depends(get_admin)):
    _id = ObjectId(_id)
    await db.events.delete_one({"_id": _id})
    return None


@router.get("/check_status", response_model=list[RegisterEvent])
async def check_status(reg_no: int, admin_reg_no: int = Depends(get_admin)):
    _data = await db.event_register.find({"reg_no": reg_no}).to_list(None)
    if _data:
        for i in range(len(_data)):
            _data[i]["screenshot_url"] = cloudinary.CloudinaryImage(_data[i]["screenshot_id"]).build_url()
    return _data


@router.get("/payment_screenshot", response_model=str)
async def get_payment_screenshot(
    _id: str = Query(alias="id"), admin_reg_no: int = Depends(get_admin)
):
    return cloudinary.CloudinaryImage(_id).build_url()


@router.get("/events/pending_verification", response_model=list[RegisterEvent])
async def pending_verification(admin_reg_no: int = Depends(get_admin)):
    _data = await db.event_register.find({"status": "pending"}).to_list(None)
    if _data:
        for i in range(len(_data)):
            _data[i]["screenshot_url"] = cloudinary.CloudinaryImage(_data[i]["screenshot_id"]).build_url()
    return _data


@router.post("/events/pending_verification")
async def pending_verification(
    data: VerifyPayment, admin_reg_no: int = Depends(get_admin)
):
    await db.event_register.update_one(
        {"reg_no": data.reg_no, "event_id": data.event_id},
        {"$set": {"status": data.status.value}},
    )
    user_data = await db.event_register.find_one({"reg_no": data.reg_no})
    event_data = await db.events.find_one({"_id": ObjectId(data.event_id)})
    if user_data and event_data:
        url = f"{os.environ['FRONTEND_DOMAIN']}/events/attendance?id={user_data['_id']}"
        qr_img = create_qr(url)
        await send([user_data['email']], f"{event_data['name']}: Payment Verified Successful", html_body=payment_verified_mail(user_data, event_data), attachments=[qr_img])
    return {"msg": "Updated successfully"}


@router.get("/events/attendance")
async def attendance(_id: str = Query(alias="id"), admin_reg_no: int = Depends(get_admin)):
    try:
        mongo_id = ObjectId(_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID"
        )
    found = await db.event_register.find_one({"_id": mongo_id})
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid ID"
        )
    if not found.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your payment still under verification"
        )
    await db.event_register.update_one({"_id": mongo_id}, {"$set": {
        "attended": True
    }})
    return None


@router.get("/export", response_model=list[Event] | list[RegisterEventWithoutScreenshotUrl])
async def export(
    collection_name: str = Query(alias="id"), admin_reg_no: int = Depends(get_admin)
):
    data = await db[collection_name].find().to_list(None)
    return data
