"""Module for rendering QR codes"""

from qrcode import QRCode
from qrcode.image.pil import PilImage

from payment_api.application.use_cases.ports import AbstractQRCodeRenderer


class QRCodeRenderer(AbstractQRCodeRenderer):
    """Concrete implementation of QR code rendering."""

    def render(self, data: str) -> bytes:
        """Render a QR code from the given data string.

        :data: str - The data to encode in the QR code.
        :return: bytes - The rendered QR code as a byte array.
        """

        qr_code = QRCode(image_factory=PilImage)
        qr_code.add_data(data)
        image = qr_code.make_image()
        return image.get_image().tobytes()
