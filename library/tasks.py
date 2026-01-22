from datetime import datetime, timedelta

from celery import shared_task, Celery
from celery.schedules import crontab
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings

app = Celery()

app.conf.beat_schedule = {
    'add-every-day': {
        'task': 'tasks.check_overdue_loans',
        'schedule': 1
    },
}
app.conf.timezone = 'UTC'

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


# @app.task(run_every=timedelta(days=1))
@app.task
def check_overdue_loans():
    try:
        loans = Loan.objects.filter(is_returned=False)
        for each in loans.iterator():
            today = datetime.now().date()
            check_current_date = each.loan_date.replace(month=today.month, year=today.year)

            check_due_date = check_current_date + timedelta(days=each.due_date)

            if today > check_due_date:
                member_email = each.member.user.email
                book_title = each.book.title
                send_mail(
                    subject='Book Loaned Overdue',
                    message=f'Hello {each.member.user.username},\n\nYou have overdue loaned "{book_title}".\n',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[member_email],
                    fail_silently=False,
                )

    except Exception as e:
        print(f"Error checking overdue loans: {e}")
