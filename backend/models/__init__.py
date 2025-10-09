# Import all models here to ensure they are registered properly
from backend.models.user import User
from backend.models.course import Course
from backend.models.registration import Registration
from backend.models.payment import Payment
from backend.models.order import Order
from backend.models.blacklisted_tokens import BlacklistedToken
from backend.models.social_post import SocialMediaPost
from backend.models.category import Category
from backend.models.family import FamilyLink
from backend.models.learning_progress import LearningProgress
from backend.models.course_module import CourseModule
from backend.models.course_lesson import CourseLesson
from backend.models.lesson_progress import LessonProgress
from backend.models.payment_receipt import PaymentReceipt

