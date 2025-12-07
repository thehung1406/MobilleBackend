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
    SMTP Mail Service — gửi email xác nhận booking cho khách.
    Clean Architecture: service tách biệt khỏi route và task.
    """

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.sender = settings.MAIL_SENDER

    # =====================================================================
    # SEND BOOKING CONFIRMATION EMAIL
    # =====================================================================

    def send_booking_confirmation(self, booking_id: int):
        """
        Gửi email cho khách sau khi đặt phòng thành công.
        """

        with Session(engine) as session:
            booking = session.get(Booking, booking_id)

            if not booking:
                logger.error(f"[MailService] Booking not found: #{booking_id}")
                return

            user = session.get(User, booking.user_id)

            rooms = session.exec(
                select(BookedRoom).where(BookedRoom.booking_id == booking_id)
            ).all()

            # Tạo HTML body
            body = self._build_booking_email_template(user, booking, rooms)

            # SMTP send
            try:
                self._send_email(
                    to=user.email,
                    subject=f"Booking Confirmation #{booking_id}",
                    html_body=body,
                )
                logger.info(f"[MailService] Email sent for booking #{booking_id}")

            except Exception as e:
                logger.error(f"[MailService] Failed to send email: {e}")

    # =====================================================================
    # INTERNAL TEMPLATE BUILDER
    # =====================================================================

    def _build_booking_email_template(self, user, booking, rooms):
        """
        Tạo HTML email content đẹp.
        """

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
            <p>— Hotel Booking System</p>
        </body>
        </html>
        """

    # =====================================================================
    # SMTP CORE SENDER
    # =====================================================================

    def _send_email(self, to: str, subject: str, html_body: str):
        """
        Gửi email HTML qua SMTP server.
        """

        msg = MIMEMultipart()
        msg["From"] = self.sender
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.sender, to, msg.as_string())

    def send_payment_success(self, booking_id: int):
        with Session(engine) as session:
            booking = session.get(Booking, booking_id)
            if not booking:
                return

            user = session.get(User, booking.user_id)

            body = f"""
            <h2>Thanh toán thành công!</h2>
            <p>Booking #{booking.id} của bạn đã được thanh toán.</p>
            """

            self._send_email(
                to=user.email,
                subject=f"Payment Success #{booking_id}",
                html_body=body,
            )

