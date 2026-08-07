import io
from typing import Optional

try:
    import qrcode
except ImportError:
    qrcode = None


def generate_qr_image(url: str) -> Optional[bytes]:
    """Generate a QR code PNG image for the given URL.
    
    Returns raw bytes of the PNG image, or None if qrcode is not installed.
    """
    if qrcode is None:
        return None

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
