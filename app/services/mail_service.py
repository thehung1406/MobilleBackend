import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import engine
from app.models.booking import Booking
from app.models.booked_room import BookedRoom
from app.models.user import User
from app.models.room import Room
from app.models.room_type import RoomType
from app.core.logger import logger


class MailService:
    """
    SMTP Mail Service — gửi email xác nhận booking và thanh toán.
    Không thay đổi cấu trúc model/repo/service của project.
    """

    def __init__(self):
        self.smtp_server = settings.MAIL_SERVER
        self.smtp_port = settings.MAIL_PORT
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.sender = settings.MAIL_FROM
        self.sender_name = settings.MAIL_FROM_NAME
        self.use_tls = settings.MAIL_STARTTLS
        self.use_ssl = settings.MAIL_SSL_TLS

    # =====================================================================
    # SEND BOOKING CONFIRMATION
    # =====================================================================

    def send_booking_confirmation(self, booking_id: int):
        with Session(engine) as session:
            booking = session.get(Booking, booking_id)
            if not booking:
                logger.error(f"[MailService] Booking not found #{booking_id}")
                return False

            user = session.get(User, booking.user_id)
            rooms = session.exec(
                select(BookedRoom).where(BookedRoom.booking_id == booking_id)
            ).all()

            html_body = self._build_booking_email_template(session, user, booking, rooms)

            try:
                self._send_email(
                    to=user.email,
                    subject=f"Booking Confirmation #{booking_id}",
                    html_body=html_body,
                )
                logger.info(f"[MailService] Booking email sent #{booking_id}")
                return True
            except Exception as e:
                logger.error(f"[MailService] Failed to send booking email: {e}")
                return False

    # =====================================================================
    # BOOKING TEMPLATE (HTML đẹp)
    # =====================================================================

    def _build_booking_email_template(self, session, user, booking, rooms):
        room_items = ""

        for r in rooms:
            room_obj = session.exec(select(Room).where(Room.id == r.room_id)).first()
            room_type = session.get(RoomType, room_obj.room_type_id)

            room_items += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{r.room_id}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{room_type.name}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{r.checkin} → {r.checkout}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{room_type.price:,} đ/đêm</td>
                </tr>
            """

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto;">

                <h2 style="color: #2b7cff;">Xin chào {user.full_name},</h2>
                <p>Cảm ơn bạn đã sử dụng hệ thống <strong>Hotel Booking</strong>.</p>

                <h3 style="margin-top: 30px;">Thông tin đặt phòng</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 8px; text-align: left;">Mã Booking</th>
                        <th style="padding: 8px; text-align: left;">Ngày tạo</th>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">#{booking.id}</td>
                        <td style="padding: 8px;">{booking.booking_date}</td>
                    </tr>
                </table>

                <h3 style="margin-top: 20px;">Chi tiết phòng</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 8px; text-align: left;">Room ID</th>
                        <th style="padding: 8px; text-align: left;">Loại Phòng</th>
                        <th style="padding: 8px; text-align: left;">Thời gian</th>
                        <th style="padding: 8px; text-align: left;">Giá</th>
                    </tr>
                    {room_items}
                </table>

                <p style="margin-top: 30px;">Nếu bạn cần hỗ trợ thêm, hãy phản hồi email này.</p>
                <p>Trân trọng,<br> <strong>{self.sender_name}</strong></p>
            </div>
        </body>
        </html>
        """
        return html

    # =====================================================================
    # SEND PAYMENT SUCCESS EMAIL
    # =====================================================================

    def send_payment_success(self, booking_id: int):
        with Session(engine) as session:
            booking = session.get(Booking, booking_id)
            if not booking:
                logger.error(f"[MailService] Payment mail failed: #{booking_id} not found")
                return False

            user = session.get(User, booking.user_id)

            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #28a745;">Thanh toán thành công!</h2>
                    <p>Booking <strong>#{booking.id}</strong> của bạn đã được thanh toán.</p>
                    <p>Cảm ơn bạn đã sử dụng dịch vụ!</p>
                </div>
            </body>
            </html>
            """

            try:
                self._send_email(
                    to=user.email,
                    subject=f"Payment Success #{booking_id}",
                    html_body=html_body,
                )
                logger.info(f"[MailService] Payment email sent #{booking_id}")
                return True

            except Exception as e:
                logger.error(f"[MailService] Failed to send payment email: {e}")
                return False

    # =====================================================================
    # SMTP CORE
    # =====================================================================

    def _send_email(self, to: str, subject: str, html_body: str):
        msg = MIMEMultipart()
        msg["From"] = f"{self.sender_name} <{self.sender}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        # SSL (Port 465)
        if self.use_ssl:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.sendmail(self.sender, to, msg.as_string())
            return

        # TLS (Port 587)
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.sender, to, msg.as_string())
