from app.worker.celery_app import celery


def enqueue_email(to: str, subject: str, html: str):
    """
    Enqueue an email to be sent asynchronously.
    """
    celery.send_task("tasks.send_email", args=[to, subject, html])


def enqueue_invoice(to: str, booking_id: str, amount: float, transaction_code: str | None = None):
    """
    Enqueue an invoice email. Accepts an optional transaction code.
    """
    if transaction_code:
        celery.send_task("tasks.send_invoice", args=[to, booking_id, amount, transaction_code])
    else:
        celery.send_task("tasks.send_invoice", args=[to, booking_id, amount])
