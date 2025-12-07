from datetime import datetime, date, timedelta
from sqlmodel import Session, select
from .celery_app import celery
from app.services.mail_service import send_mail
from app.models.booking import Booking
from app.models.payment import Payment
from app.utils.enums import BookingStatus
from app.core.database import engine

@celery.task(name="tasks.send_email")
def send_email(to: str, subject: str, html: str):
    send_mail(to, subject, html)


@celery.task(name="tasks.send_booking_confirmation")
def send_booking_confirmation(
    guest_email: str, 
    guest_name: str, 
    booking_id: str, 
    room_number: str,
    check_in: str, 
    check_out: str, 
    guests: int, 
    total_amount: float,
    special_requests: str = None
):
    """
    Send booking confirmation email to guest.
    """
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">🏨 Grand Palace Hotel</h1>
            <p style="color: white; margin: 10px 0 0 0;">Booking Confirmation</p>
        </div>
        
        <div style="padding: 30px; background: #f9f9f9;">
            <h2 style="color: #333;">Dear {guest_name},</h2>
            <p style="color: #666; line-height: 1.6;">
                Thank you for choosing Grand Palace Hotel! Your booking has been confirmed and is currently being processed by our staff.
            </p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">Booking Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">Booking ID:</td>
                        <td style="padding: 8px 0; color: #333;">{booking_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">Room:</td>
                        <td style="padding: 8px 0; color: #333;">Room {room_number}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">Check-in:</td>
                        <td style="padding: 8px 0; color: #333;">{check_in}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">Check-out:</td>
                        <td style="padding: 8px 0; color: #333;">{check_out}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">Guests:</td>
                        <td style="padding: 8px 0; color: #333;">{guests}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-weight: bold;">Total Amount:</td>
                        <td style="padding: 8px 0; color: #333; font-size: 18px; font-weight: bold;">${total_amount:.2f}</td>
                    </tr>
                </table>
                
                {f'<div style="margin-top: 15px;"><strong style="color: #666;">Special Requests:</strong><br><span style="color: #333;">{special_requests}</span></div>' if special_requests else ''}
            </div>
            
            <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="color: #1976d2; margin: 0 0 10px 0;">📋 Next Steps</h4>
                <ul style="color: #666; margin: 0; padding-left: 20px;">
                    <li>Our staff will review and confirm your booking within 24 hours</li>
                    <li>You will receive a confirmation email once approved</li>
                    <li>Please arrive at the hotel after 3:00 PM on your check-in date</li>
                    <li>Check-out time is 11:00 AM</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <p style="color: #666;">Need help? Contact us:</p>
                <p style="color: #333; margin: 5px 0;">📞 +1 (555) 123-4567</p>
                <p style="color: #333; margin: 5px 0;">✉️ info@grandpalacehotel.com</p>
            </div>
        </div>
        
        <div style="background: #333; padding: 20px; text-align: center;">
            <p style="color: #999; margin: 0; font-size: 12px;">
                © 2025 Grand Palace Hotel. All rights reserved.
            </p>
        </div>
    </div>
    """
    send_mail(guest_email, "🏨 Booking Confirmation - Grand Palace Hotel", html)


@celery.task(name="tasks.send_booking_approved")
def send_booking_approved(
    guest_email: str, 
    guest_name: str, 
    booking_id: str, 
    room_number: str,
    check_in: str, 
    check_out: str
):
    """
    Send booking approval email to guest.
    """
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">✅ Booking Confirmed!</h1>
            <p style="color: white; margin: 10px 0 0 0;">Grand Palace Hotel</p>
        </div>
        
        <div style="padding: 30px; background: #f9f9f9;">
            <h2 style="color: #333;">Great news, {guest_name}!</h2>
            <p style="color: #666; line-height: 1.6;">
                Your booking has been <strong>approved</strong> and confirmed. We're excited to welcome you to Grand Palace Hotel!
            </p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4caf50;">
                <h3 style="color: #333; margin-top: 0;">Confirmed Booking</h3>
                <p style="color: #666; margin: 5px 0;"><strong>Booking ID:</strong> {booking_id}</p>
                <p style="color: #666; margin: 5px 0;"><strong>Room:</strong> Room {room_number}</p>
                <p style="color: #666; margin: 5px 0;"><strong>Check-in:</strong> {check_in} (after 3:00 PM)</p>
                <p style="color: #666; margin: 5px 0;"><strong>Check-out:</strong> {check_out} (before 11:00 AM)</p>
            </div>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="color: #2e7d32; margin: 0 0 10px 0;">🎉 You're all set!</h4>
                <p style="color: #666; margin: 0;">
                    Just show up on your check-in date with a valid ID. We'll take care of the rest!
                </p>
            </div>
        </div>
    </div>
    """
    send_mail(guest_email, "✅ Booking Approved - Grand Palace Hotel", html)


@celery.task(name="tasks.send_invoice")
def send_invoice(to: str, booking_id: str, amount: float, transaction_code: str | None = None):
    """
    Send a more detailed payment receipt email.

    Includes the booking identifier, optional transaction code, amount and date.
    """
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    html = (
        f"<h3>Payment Receipt</h3>"
        f"<p><strong>Booking ID:</strong> {booking_id}</p>"
        f"{f'<p><strong>Transaction:</strong> {transaction_code}</p>' if transaction_code else ''}"
        f"<p><strong>Amount:</strong> ${amount:.2f}</p>"
        f"<p><strong>Date:</strong> {date_str}</p>"
    )
    send_mail(to, "Your Hotel Payment Receipt", html)


@celery.task(name="tasks.auto_update_bookings")
def auto_update_bookings():
    """
    Periodic task to automatically update booking statuses.

    - Cancel bookings where check_in has passed and the status is pending or confirmed.
    - Complete bookings where check_out has passed and the status is confirmed.
    """
    today = date.today()
    with Session(engine) as session:
        # Cancel overdue bookings
        overdue = session.exec(
            select(Booking).where(
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                Booking.check_in < today,
            )
        ).all()
        for b in overdue:
            b.status = BookingStatus.CANCELLED
            session.add(b)

        # Complete finished bookings
        completed = session.exec(
            select(Booking).where(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.check_out < today,
            )
        ).all()
        for b in completed:
            b.status = BookingStatus.COMPLETED
            session.add(b)

        session.commit()
