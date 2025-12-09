import qrcode
import base64
from io import BytesIO


def generate_qr_base64(data: str) -> str:
    """
    Generate QR Code và trả về dạng Base64 PNG.
    FE chỉ cần <img src="data:image/png;base64,..." />
    """
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    base64_qr = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return base64_qr
