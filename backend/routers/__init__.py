from fastapi import APIRouter
from backend.routers.course import router as course_router
from backend.routers.payment import router as payment_router
from backend.routers.registration import router as registration_router
from backend.routers.pages import router as pages_router
from backend.routers.auth import auth_router
from backend.routers.order import router as orders_router
from backend.routers.paystack import router as paystack_router
from backend.routers.admin_courses import router as admin_router
from backend.routers.admin_customers import router as admin_customers_router
from backend.routers.admin_registrations import router as admin_registrations_router
from backend.routers.admin_payments import router as admin_payments_router
from backend.routers.social_media import router as social_media_router
from backend.routers.teacher_application import router as teacher_app_router
from backend.routers.testimonial import router as testimonial_router
from backend.routers.category import router as category_router

# API Router for backend endpoints
api_router = APIRouter()
api_router.include_router(course_router, prefix="/courses", tags=["courses"])
api_router.include_router(payment_router, prefix="/payments", tags=["payments"])
api_router.include_router(registration_router, prefix="/registrations", tags=["registration"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(paystack_router, tags=["paystack"])
api_router.include_router(auth_router, prefix="/auth", tags=["paystack"])
api_router.include_router(admin_router)
api_router.include_router(admin_customers_router)
api_router.include_router(admin_registrations_router)
api_router.include_router(admin_payments_router)
api_router.include_router(social_media_router)
api_router.include_router(teacher_app_router, tags=["teacher_applications"])
api_router.include_router(testimonial_router, tags=["testimonials"])
api_router.include_router(category_router)

# Export both routers
__all__ = ["api_router","pages_router"]

