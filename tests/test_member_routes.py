import unittest
from app import create_app
from app.db import db
from app.members.models import Member

class TestRoutes(unittest.TestCase):

    def setUp(self):
        # Create a test Flask application
        self.app = create_app('test')
        self.client = self.app.test_client()

        # Initialize the database
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Clean up the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_route(self):
        # Test the home route
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register_route(self):
        # Test the register route with valid data
        response = self.client.post('/register', data={
            'name': 'Test User',
            'id_number': '12345678',
            'phone_number': '123456789',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirects after successful registration

    def test_login_route(self):
        # Test the login route with valid credentials
        member = Member(name='Test User', id_number='12345678', phone_number='123456789', password='testpassword')
        with self.app.app_context():
            db.session.add(member)
            db.session.commit()
        response = self.client.post('/login', data={
            'id_number': '12345678',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertIn(b'Login successful.', response.data)


if __name__ == '__main__':
    unittest.main()
