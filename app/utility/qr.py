import segno
from PIL import Image
import io


def create_qr(data: str):
    qr = io.BytesIO()
    segno.make_qr(data).save(qr, kind="png", scale=8)
    qr.seek(0)
    img = Image.open(qr)
    img = img.convert('RGB')
    img_width, img_height = img.size
    logo_max_size = img_height // 3
    logo_img = Image.open('./acm_sist_logo.png')
    logo_img.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
    box = ((img_width - logo_img.size[0]) // 2, (img_height - logo_img.size[1]) // 2)
    img.paste(logo_img, box)
    # qr.to_artistic(background='static/Images/horizon24.gif', target=img, scale=8, kind="gif")
    return img
