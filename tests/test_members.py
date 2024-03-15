import unittest
from app.db import db
from app.members.models import Member
from app import create_app

class TestMemberModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()

        # Establish application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create all database tables
        db.create_all()

    def tearDown(self):
        # Remove database session and drop all tables
        db.session.remove()
        db.drop_all()

        # Pop application context
        self.app_context.pop()

    # Your test cases go here

    def test_create_member(self):
        member = Member(name="John Doe", id_number=123456, phone_number="1234567890", password="password123")
        db.session.add(member)
        db.session.commit()
        self.assertIsNotNone(member.id)

    def test_password_hashing(self):
        password = "password123"
        member = Member(name="John Doe", id_number=123456, phone_number="1234567890", password=password)
        db.session.add(member)
        db.session.commit()
        self.assertNotEqual(member.password_hash, password)

    def test_password_verification(self):
        password = "password123"
        member = Member(name="John Doe", id_number=123456, phone_number="1234567890", password=password)
        db.session.add(member)
        db.session.commit()
        self.assertTrue(member.check_password(password))

    def test_unique_id_number_constraint(self):
        member1 = Member(name="John Doe", id_number=123456, phone_number="1234567890", password="password123")
        member2 = Member(name="Jane Doe", id_number=123456, phone_number="9876543210", password="password123")
        db.session.add(member1)
        db.session.add(member2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_unique_phone_number_constraint(self):
        member1 = Member(name="John Doe", id_number=123456, phone_number="1234567890", password="password123")
        member2 = Member(name="Jane Doe", id_number=123457, phone_number="1234567890", password="password123")
        db.session.add(member1)
        db.session.add(member2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_regular_fee_payment(self):
        member = Member(name="John Doe", id_number=123456, phone_number="1234567890", password="password123")
        db.session.add(member)
        db.session.commit()
        member.reg_fee_paid = True
        db.session.commit()
        self.assertTrue(member.reg_fee_paid)

    def test_admin_privileges(self):
        member = Member(name="John Doe", id_number=123456, phone_number="1234567890", password="password123")
        db.session.add(member)
        db.session.commit()
        member.is_admin = True
        db.session.commit()
        self.assertTrue(member.is_admin)

    def test_account_activation(self):
        member = Member(name="John Doe", id_number=123456, phone_number="1234567890", password="password123")
        db.session.add(member)
        db.session.commit()
        member.is_active = True
        db.session.commit()
        self.assertTrue(member.is_active)

if __name__ == '__main__':
    unittest.main()
