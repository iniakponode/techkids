import os
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.crud import crud_course, crud_registration, crud_order
from backend.core.database import get_db
from backend.models.user import User
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

## 3.6 Admin Dashboard Route
@router.get("/admin/dashboard")
async def admin_dashboard(request: Request, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "user": user, "current_user": user})

@router.get("/admin/manage-courses", name="manage_courses")
async def manage_courses_page(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Render the 'Manage Courses' page for admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    courses = crud_course.get_all(db=db)
    return templates.TemplateResponse("admin/manage_courses.html", {"request": request, "courses": courses, "current_user": user})

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

@router.get("/admin/coming_soon", response_class=HTMLResponse)
async def admin_coming_soon(request: Request, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return templates.TemplateResponse("admin/coming_soon.html", {"request": request, "current_user": user})