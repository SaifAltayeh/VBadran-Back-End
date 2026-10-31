import secrets
from datetime import timedelta

from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile, User

from .models import Order, OrderItem, Payment, Subscription


def make_order_number() -> str:
    return "VB" + timezone.now().strftime("%y%m%d") + secrets.token_hex(3).upper()


@transaction.atomic
def create_pending_order(*, full_name, email, phone, country, program, package, terms_accepted, user=None):
    product = package or program
    if product is None:
        raise ValueError("Choose a program or package.")
    title = package.name if package is not None else program.title
    order = Order.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        order_number=make_order_number(),
        full_name=full_name,
        email=email,
        phone=phone or "",
        country=country or "",
        program=program,
        package=package,
        amount=product.price,
        currency=product.currency,
        status=Order.Status.PENDING,
        terms_accepted=terms_accepted,
    )
    OrderItem.objects.create(order=order, title=title, amount=product.price)
    Payment.objects.create(
        order=order,
        provider="unconfigured",
        amount=product.price,
        currency=product.currency,
        status=Payment.Status.PENDING,
    )
    return order


@transaction.atomic
def fulfill_paid_order(order: Order, provider: str = "manual", transaction_id: str = ""):
    """Grant access after a payment provider confirms the charge.

    Public checkout does not call this. Wire it from the provider webhook
    or from the admin action once a transaction is verified.
    """
    if order.status == Order.Status.PAID and Subscription.objects.filter(order=order).exists():
        return order.user

    user = order.user or User.objects.filter(email__iexact=order.email).first()
    temporary_password = None
    if user is None:
        temporary_password = secrets.token_urlsafe(9)
        parts = order.full_name.strip().split(" ", 1)
        user = User.objects.create_user(
            email=order.email,
            password=temporary_password,
            first_name=parts[0] if parts else "",
            last_name=parts[1] if len(parts) > 1 else "",
        )

    profile, _ = Profile.objects.get_or_create(user=user)
    if order.phone and not profile.phone:
        profile.phone = order.phone
    if order.country and not profile.country:
        profile.country = order.country
    profile.save()

    order.user = user
    order.status = Order.Status.PAID
    order.save(update_fields=["user", "status", "updated_at"])

    payment = order.payments.order_by("-created_at").first()
    if payment is None:
        payment = Payment(order=order, amount=order.amount, currency=order.currency)
    payment.provider = provider
    payment.transaction_id = transaction_id
    payment.status = Payment.Status.PAID
    payment.save()

    program = order.program
    if program is None and order.package_id and order.package.program_id:
        program = order.package.program

    if program is not None:
        start = timezone.localdate()
        weeks = order.package.duration_weeks if order.package_id else program.duration_weeks
        Subscription.objects.update_or_create(
            order=order,
            defaults={
                "user": user,
                "program": program,
                "status": Subscription.Status.ACTIVE,
                "start_date": start,
                "end_date": start + timedelta(weeks=weeks),
                "coach_note": "Your plan is ready. Train the sessions as written and send your weekly check-in.",
            },
        )

    lines = [f"Your VBADRAN order {order.order_number} is confirmed."]
    if program is not None:
        lines.append(f"Program: {program.title}")
    if temporary_password:
        lines.append(f"An account was created for {user.email}.")
        lines.append(f"Temporary password: {temporary_password}")
        lines.append("Sign in and change it from your account page.")
    send_mail(
        subject=f"VBADRAN order {order.order_number}",
        message="\n".join(lines),
        from_email=None,
        recipient_list=[user.email],
        fail_silently=True,
    )
    return user
