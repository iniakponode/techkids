import os
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import math
from backend.crud import crud_course, crud_registration, crud_order, crud_user, crud_payment
from backend.core.database import get_db
from backend.models.user import User
from backend.models.payment import Payment
from backend.models.registration import Registration
from backend.models.order import Order
from backend.models.course import Course
from backend.routers.auth import get_current_user

router = APIRouter()

# Setup Jinja2 templates
templates_folder_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "templates")
templates = Jinja2Templates(directory=templates_folder_path)

@router.get("/", name="home")
def home(request: Request, db: Session = Depends(get_db)):
    """Render the home page with courses"""
    courses = crud_course.get_all(db=db)
    return templates.TemplateResponse(
        "pages/index.html", 
        {"request": request, "courses": courses}
    )

@router.get("/registration", name="registration")
def registration_page(request: Request, db: Session = Depends(get_db)):
    """Render the registration page with courses"""
    courses = crud_course.get_all(db=db)
    selected_course_id = request.query_params.get('course')
    return templates.TemplateResponse(
        "pages/registration.html", 
        {
            "request": request, 
            "courses": courses,
            "selected_course_id": selected_course_id
        }
    )

# @router.get("/payment", name="payment")
# def payment_page(request: Request, db: Session = Depends(get_db)):
#     """Render the payment page with registration data"""
#     registration_id = request.query_params.get('registration')
#     registration = None
#     if registration_id:
#         registration = crud_registration.get_by_id(db=db, registration_id=int(registration_id))
    
#     return templates.TemplateResponse(
#         "pages/payment.html", 
#         {
#             "request": request,
#             "registration": registration
#         }
#     )
    
@router.get("/payment", name="payment")
def payment_page(request: Request, order: int, db: Session = Depends(get_db)):
    """
    Render the payment page for a specific order.
    Shows total amount, status, and a "Pay Now" button.
    """
    order_obj = crud_order.get_by_id(db, order_id=order)
    if not order_obj:
        raise HTTPException(status_code=404, detail="Order not found")

    # We'll pass the Order info to our template
    return templates.TemplateResponse(
        "pages/payment.html",
        {"request": request, "order": order_obj}
    )
    
# @router.get("/admin/add-course", name="add_course_form")
# def add_course_page(request: Request):
#     """
#     Render the 'Add Course' page.
#     """
#     return templates.TemplateResponse(
#         "admin/add_course.html",
#         {"request": request}
#     )

@router.get("/admin/register", name="admin-register-form")
async def admin_register_page(request: Request, 
                              user: User = Depends(get_current_user)
                              ):
    return templates.TemplateResponse("admin/admin_register.html", {"request": request, 
                                                                    "current_user": user
                                                                    })

@router.get("/login", name="login-form")
async def login_page(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})

@router.get("/logout", name="logout-form")
async def logout_page(request: Request):
    return templates.TemplateResponse("logout.html", {"request": request})

@router.get("/contact", name="contact")
async def contact_page(request: Request):
    """Render the contact page."""
    return templates.TemplateResponse("pages/contact.html", {"request": request})

## 3.6 Admin Dashboard Route
@router.get("/admin/dashboard")
async def admin_dashboard(request: Request, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "user": user, "current_user": user})

@router.get("/admin/manage-courses", name="manage_courses")
async def manage_courses_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    """Render the 'Manage Courses' page for admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    skip = (page - 1) * limit
    query = db.query(Course)
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))
    total_count = query.count()
    courses = query.offset(skip).limit(limit).all()
    total_pages = math.ceil(total_count / limit) if limit else 1
    has_next = page < total_pages
    start_page = max(1, page - 2)
    end_page = min(total_pages, start_page + 3)
    if end_page - start_page < 3:
        start_page = max(1, end_page - 3)
    pages = list(range(start_page, end_page + 1))
    return templates.TemplateResponse(
        "admin/manage_courses.html",
        {
            "request": request,
            "courses": courses,
            "current_user": user,
            "page": page,
            "limit": limit,
            "has_next": has_next,
            "pages": pages,
            "search": search,
        },
    )


@router.get("/admin/manage-registrations", name="manage_registrations")
async def manage_registrations_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    """Render the 'Manage Registrations' page for admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    skip = (page - 1) * limit
    query = db.query(Registration)
    if search:
        query = query.filter(Registration.fullName.ilike(f"%{search}%"))
    total_count = query.count()
    regs = query.offset(skip).limit(limit).all()
    registrations = []
    for reg in regs:
        payment = db.query(Payment).filter(Payment.order_id == reg.order_id).first()
        courses_count = (
            db.query(Registration)
            .filter(Registration.user_id == reg.user_id)
            .count()
        )
        registrations.append(
            {
                "id": reg.id,
                "fullName": reg.fullName,
                "phone": reg.phone,
                "user_id": reg.user_id,
                "course_id": reg.course_id,
                "order_id": reg.order_id,
                "courses_count": courses_count,
                "payment_status": payment.status if payment else "pending",
            }
        )
    total_pages = math.ceil(total_count / limit) if limit else 1
    has_next = page < total_pages
    start_page = max(1, page - 2)
    end_page = min(total_pages, start_page + 3)
    if end_page - start_page < 3:
        start_page = max(1, end_page - 3)
    pages = list(range(start_page, end_page + 1))
    return templates.TemplateResponse(
        "admin/manage_registrations.html",
        {
            "request": request,
            "registrations": registrations,
            "current_user": user,
            "page": page,
            "limit": limit,
            "has_next": has_next,
            "pages": pages,
            "search": search,
        },
    )


@router.get("/admin/customer-courses/{user_id}", name="customer_courses")
async def customer_courses_page(
    request: Request,
    user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Display all courses a customer registered for."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    customer = db.query(User).filter(User.id == user_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    regs = db.query(Registration).filter(Registration.user_id == user_id).all()
    courses = []
    total_amount = 0.0
    for reg in regs:
        course = db.query(Course).filter(Course.id == reg.course_id).first()
        if course:
            courses.append(
                {
                    "name": course.title,
                    "course_id": course.id,
                    "registered_at": reg.registered_at,
                    "price": course.price,
                }
            )
            total_amount += course.price

    return templates.TemplateResponse(
        "admin/customer_courses.html",
        {
            "request": request,
            "customer": customer,
            "courses": courses,
            "total_amount": total_amount,
            "current_user": user,
        },
    )


@router.get("/admin/manage-payments", name="manage_payments")
async def manage_payments_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    order: int | None = None,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    """Render the 'Manage Payments' page for admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    skip = (page - 1) * limit
    query = db.query(Payment)
    if order:
        query = query.filter(Payment.order_id == order)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Payment.transaction_id.ilike(like)
        )
    total_count = query.count()
    payments_db = query.offset(skip).limit(limit).all()

    payments = []
    for p in payments_db:
        order_obj = db.query(Order).filter(Order.id == p.order_id).first()
        user_obj = db.query(User).filter(User.id == order_obj.user_id).first() if order_obj else None
        courses_count = db.query(Registration).filter(Registration.order_id == p.order_id).count()
        first_reg = (
            db.query(Registration)
            .filter(Registration.order_id == p.order_id)
            .first()
        )
        payments.append(
            {
                "id": p.id,
                "transaction_id": p.transaction_id,
                "amount": p.amount,
                "status": p.status,
                "payment_date": p.payment_date,
                "customer_name": first_reg.fullName if first_reg else "",
                "customer_email": user_obj.email if user_obj else "",
                "courses_count": courses_count,
            }
        )

    total_pages = math.ceil(total_count / limit) if limit else 1
    has_next = page < total_pages
    start_page = max(1, page - 2)
    end_page = min(total_pages, start_page + 3)
    if end_page - start_page < 3:
        start_page = max(1, end_page - 3)
    pages = list(range(start_page, end_page + 1))
    return templates.TemplateResponse(
        "admin/manage_payments.html",
        {
            "request": request,
            "payments": payments,
            "current_user": user,
            "page": page,
            "limit": limit,
            "has_next": has_next,
            "pages": pages,
            "search": search,
            "order": order,
        },
    )


@router.get("/admin/manage-customers", name="manage_customers")
async def manage_customers_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    """Render the 'Manage Customers' page for admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    skip = (page - 1) * limit
    query = db.query(User)
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    total_count = query.count()
    customers = query.offset(skip).limit(limit).all()
    total_pages = math.ceil(total_count / limit) if limit else 1
    has_next = page < total_pages
    start_page = max(1, page - 2)
    end_page = min(total_pages, start_page + 3)
    if end_page - start_page < 3:
        start_page = max(1, end_page - 3)
    pages = list(range(start_page, end_page + 1))
    return templates.TemplateResponse(
        "admin/manage_customers.html",
        {
            "request": request,
            "customers": customers,
            "current_user": user,
            "page": page,
            "limit": limit,
            "has_next": has_next,
            "pages": pages,
            "search": search,
        },
    )

@router.get("/admin/add-course", name="add_course_form")
async def add_course_page(request: Request, user: User = Depends(get_current_user)):
    """Render the 'Add Course' page."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return templates.TemplateResponse("admin/add_course.html", {"request": request, "current_user": user})

@router.get("/admin/edit-course/{course_id}", name="edit_course_form")
async def edit_course_page(request: Request, course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Render the 'Edit Course' page."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    course = crud_course.get_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return templates.TemplateResponse("admin/admin_edit_course.html", {"request": request, "course": course, "current_user": user})


@router.get("/admin/edit-customer/{user_id}", name="edit_customer_form")
async def edit_customer_page(
    request: Request,
    user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    customer = crud_user.get_by_id(db, user_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return templates.TemplateResponse(
        "admin/admin_edit_customer.html",
        {"request": request, "customer": customer, "current_user": user},
    )

@router.get("/admin/coming_soon", response_class=HTMLResponse)
async def admin_coming_soon(request: Request, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return templates.TemplateResponse("admin/coming_soon.html", {"request": request, "current_user": user})