from backend.crud.course import crud_course
from backend.crud.registration import crud_registration
from backend.crud.payment import crud_payment
from backend.crud.user import crud_user
from backend.crud.order import crud_order
from backend.crud.social_post import crud_social_post

__all__ = [
    "crud_course",
    "crud_registration",
    "crud_payment",
    "crud_user",
    "crud_order"
    ,"crud_social_post"
]

