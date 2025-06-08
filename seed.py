import random
from datetime import datetime
from faker import Faker
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.user import User
from backend.models.course import Course
from backend.models.order import Order
from backend.models.registration import Registration
from backend.models.payment import Payment

from passlib.hash import bcrypt

fake = Faker()

def seed_users(db: Session, num_users: int = 50):
    """
    Populate the 'users' table with fake data.
    (No 'username' field, just 'email'.)
    """
    users = []
    for _ in range(num_users):
        is_verified = random.choice([True, False])
        user = User(
            email=fake.unique.email(),
            password_hash=bcrypt.hash("password123"),  # Default password
            role=random.choice(["student", "admin", "parent", "teacher", "organisation"]),
            is_active=random.choices([True, False], weights=[80, 20])[0],
            is_verified=is_verified,
            verification_token=None if is_verified else fake.uuid4(),
            password_reset_token=fake.uuid4() if random.choice([True, False]) else None,
            created_at=fake.date_time_between(start_date='-2y', end_date='now')
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"Seeded {num_users} users.")
    return users

def seed_courses(db: Session, num_courses: int = 20):
    """
    Populate the 'courses' table with fake data.
    """
    courses = []
    for _ in range(num_courses):
        course = Course(
            title=fake.unique.catch_phrase(),
            image_url=fake.image_url() if random.choice([True, False]) else None,
            summary=fake.sentence(nb_words=12),
            description=fake.paragraph(nb_sentences=5),
            price=round(random.uniform(50, 500), 2),
            age_group=random.choice(["Kids", "Teens", "Adults", "Seniors"]),
            duration=random.choice(["4 weeks", "6 weeks", "8 weeks", "12 weeks", "6 months"]),
            rating=round(random.uniform(0.0, 5.0), 1)
        )
        db.add(course)
        courses.append(course)
    
    db.commit()
    print(f"Seeded {num_courses} courses.")
    return courses

def seed_orders(db: Session, users: list, num_orders: int = 30):
    """
    Create 'Order' records, each linked to a random user.
    Set total_amount=0.0; status can be 'pending', 'paid', or 'cancelled'.
    """
    orders = []
    possible_statuses = ["pending", "paid", "cancelled"]
    for _ in range(num_orders):
        user = random.choice(users)
        order = Order(
            user_id=user.id,
            total_amount=0.0, 
            status=random.choice(possible_statuses),
            created_at=fake.date_time_between(start_date='-1y', end_date='now')
        )
        db.add(order)
        orders.append(order)
    db.commit()
    print(f"Seeded {num_orders} orders.")
    return orders

def seed_registrations(db: Session, orders: list, courses: list):
    """
    For each Order, create between 1 to 4 Registrations, referencing
    the same user_id as the Order owner and a random course.
    'Registration' no longer has an 'email' field, so we remove that.
    """
    total_registrations_created = 0
    statuses = ["pending", "confirmed", "cancelled"]
    verification_statuses = ["pending", "verified", "failed"]

    for order in orders:
        num_regs = random.randint(1, 4)
        order_total = 0.0

        for _ in range(num_regs):
            course = random.choice(courses)
            is_verified = random.choice(verification_statuses)

            registration = Registration(
                fullName=fake.name(),
                phone=fake.phone_number(),
                course_id=course.id,
                user_id=order.user_id,  # same user as the order
                order_id=order.id,
                registered_at=fake.date_time_between(start_date='-1y', end_date='now'),
                status=random.choice(statuses),
                is_verified=is_verified
            )
            db.add(registration)
            total_registrations_created += 1

            # Accumulate course price
            order_total += course.price

        # update the order's total_amount
        order.total_amount += order_total

    db.commit()
    print(f"Created {total_registrations_created} registrations and updated orders' totals.")
    return total_registrations_created

def seed_payments(db: Session, orders: list, num_payments: int = 20):
    """
    Populate the 'payments' table with fake data,
    referencing 'order_id'. If status='completed', set order.status='paid'.
    """
    payment_statuses = ["pending", "completed", "failed"]
    created_payments = 0

    for _ in range(num_payments):
        order = random.choice(orders)

        # Skip if it's already paid, with some probability
        if order.status == "paid" and random.random() < 0.5:
            continue

        status = random.choice(payment_statuses)
        new_payment = Payment(
            order_id=order.id,
            transaction_id=fake.uuid4(),
            amount=order.total_amount,
            status=status,
            payment_date=fake.date_time_between(start_date='-1y', end_date='now')
        )
        db.add(new_payment)
        created_payments += 1

        if status == "completed":
            order.status = "paid"

    db.commit()
    print(f"Seeded {created_payments} payments.")
    return created_payments

def seed_database():
    """
    Main function to seed the database with sample data in the new schema:
    - No 'username' in User
    - No 'email' in Registration
    - Payment references Order, Registration references Order & User
    """
    db = SessionLocal()
    try:
        print("Seeding Users...")
        users = seed_users(db, num_users=50)
        
        print("Seeding Courses...")
        courses = seed_courses(db, num_courses=20)
        
        print("Seeding Orders...")
        orders = seed_orders(db, users, num_orders=30)
        
        print("Seeding Registrations...")
        seed_registrations(db, orders, courses)
        
        print("Seeding Payments...")
        seed_payments(db, orders, num_payments=20)
        
        print("Database successfully seeded!")
    except Exception as e:
        db.rollback()
        print(f"An error occurred during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()