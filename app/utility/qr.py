import segno
from PIL import Image
import io


def create_qr(data: str):
    img = io.BytesIO()
    segno.make_qr(data).save(img, kind="png", scale=8)
    # qr.to_artistic(background='static/Images/horizon24.gif', target=img, scale=8, kind="gif")
    return img
