import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import engine
from app.models.booking import Booking
from app.models.booked_room import BookedRoom
from app.models.user import User
from app.core.logger import logger


class MailService:
    """
    SMTP Mail Service — gửi email xác nhận booking và thanh toán.
    """

    def __init__(self):
        # DÙNG ĐÚNG FIELD TRONG .env VÀ settings.py CỦA BẠN
        self.smtp_server = settings.MAIL_SERVER
        self.smtp_port = settings.MAIL_PORT
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.sender = settings.MAIL_FROM
        self.sender_name = settings.MAIL_FROM_NAME
        self.use_tls = settings.MAIL_STARTTLS
        self.use_ssl = settings.MAIL_SSL_TLS

    # =====================================================================
    # GỬI EMAIL XÁC NHẬN BOOKING
    # =====================================================================

    def send_booking_confirmation(self, booking_id: int):
        with Session(engine) as session:
            booking = session.get(Booking, booking_id)

            if not booking:
                logger.error(f"[MailService] Booking not found: #{booking_id}")
                return

            user = session.get(User, booking.user_id)

            rooms = session.exec(
                select(BookedRoom).where(BookedRoom.booking_id == booking_id)
            ).all()

            html_body = self._build_booking_email_template(user, booking, rooms)

            try:
                self._send_email(
                    to=user.email,
                    subject=f"Booking Confirmation #{booking_id}",
                    html_body=html_body,
                )
                logger.info(f"[MailService] Email sent for booking #{booking_id}")

            except Exception as e:
                logger.error(f"[MailService] Failed to send email: {e}")

    # =====================================================================
    # TEMPLATE
    # =====================================================================

    def _build_booking_email_template(self, user, booking, rooms):
        room_list = "".join(
            [
                f"<li>Room {r.room_id}: {r.checkin} → {r.checkout}, Price: {r.price}</li>"
                for r in rooms
            ]
        )

        return f"""
        <html>
        <body>
            <h2>Xin chào {user.full_name},</h2>

            <p>Bạn đã đặt phòng thành công tại hệ thống Hotel Booking!</p>

            <h3>Thông tin đặt phòng:</h3>
            <ul>
                <li><strong>Mã Booking:</strong> {booking.id}</li>
                <li><strong>Ngày tạo:</strong> {booking.booking_date}</li>
            </ul>

            <h3>Chi tiết phòng:</h3>
            <ul>
                {room_list}
            </ul>

            <p>Cảm ơn bạn đã sử dụng dịch vụ!</p>
            <p>— {self.sender_name}</p>
        </body>
        </html>
        """

    # =====================================================================
    # SMTP CORE
    # =====================================================================

    def _send_email(self, to: str, subject: str, html_body: str):
        msg = MIMEMultipart()
        msg["From"] = f"{self.sender_name} <{self.sender}>"
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html"))

        # TLS
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()

            server.login(self.username, self.password)
            server.sendmail(self.sender, to, msg.as_string())

    # =====================================================================
    # SEND PAYMENT SUCCESS
    # =====================================================================

    def send_payment_success(self, booking_id: int):
        with Session(engine) as session:
            booking = session.get(Booking, booking_id)
            if not booking:
                return

            user = session.get(User, booking.user_id)

            html_body = f"""
            <h2>Thanh toán thành công!</h2>
            <p>Booking #{booking.id} của bạn đã được thanh toán.</p>
            """

            self._send_email(
                to=user.email,
                subject=f"Payment Success #{booking_id}",
                html_body=html_body,
            )
