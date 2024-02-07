import segno
import io


def create_qr(data: str):
    img = io.BytesIO()
    qr = segno.make_qr(data)
    qr.to_artistic(background='static/Images/horizon24.gif', target=img, scale=8, kind="gif")
    return img
