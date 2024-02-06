import os
import pytz
import motor.motor_asyncio
import cloudinary
from dotenv import load_dotenv

load_dotenv()
db_client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"), ssl=True)
db = db_client.horizon24
cloudinary.config(
    cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
    api_key=os.environ["CLOUDINARY_API_KEY"],
    api_secret=os.environ["CLOUDINARY_API_SECRET"],
)
IST = pytz.timezone("Asia/Kolkata")
