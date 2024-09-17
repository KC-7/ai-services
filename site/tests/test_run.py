# tests/test_run.py

import unittest
import os
from unittest.mock import patch

# Set FLASK_DEBUG to disable Flask-Talisman during tests
os.environ['FLASK_DEBUG'] = '0'
os.environ['TESTING'] = 'True'

from run import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transform Your Business with AI', response.data)

    def test_about_page(self):
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    def test_contact_page_get(self):
        response = self.app.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Contact Us', response.data)

    def test_contact_form_submission_success(self):
        with patch('run.mail.send') as mock_send:
            response = self.app.post('/submit-contact-form', data={
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'message': 'This is a test message.'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your message has been sent successfully!', response.data)
            mock_send.assert_called_once()

    def test_contact_form_submission_failure(self):
        response = self.app.post('/submit-contact-form', data={
            'name': '',
            'email': 'invalid-email',
            'phone': '1234567890',
            'message': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error in Name: This field is required.', response.data)
        self.assertIn(b'Error in Email: Invalid email address.', response.data)
        self.assertIn(b'Error in Message: This field is required.', response.data)

    def test_services_page(self):
        response = self.app.get('/services')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Services Tailored for Your Business', response.data)

    def test_blog_list_page(self):
        response = self.app.get('/blog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our Blog', response.data)

    def test_blog_post_page_found(self):
        # Assuming there's a blog with slug 'test-blog'
        with patch('run.load_blog_data') as mock_load_blog_data:
            mock_load_blog_data.return_value = [{
                'slug': 'test-blog',
                'title': 'Test Blog',
                'date': '2024-01-01',
                'excerpt': 'This is a test blog.',
                'image': 'test_blog.jpg',
                'content': '<p>Test blog content.</p>'
            }]
            response = self.app.get('/blog/test-blog')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Blog', response.data)
            self.assertIn(b'Test blog content.', response.data)

    def test_blog_post_page_not_found(self):
        response = self.app.get('/blog/non-existent-slug', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Blog post not found.', response.data)
        self.assertIn(b'Our Blog', response.data)

    def test_chatbot_api_success(self):
        with patch('run.openai.ChatCompletion.create') as mock_chat_completion:
            mock_chat_completion.return_value = {
                'choices': [{
                    'message': {
                        'content': 'This is a test response.'
                    }
                }]
            }
            response = self.app.post('/chatbot', json={'message': 'Hello'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'response': 'This is a test response.'})

    def test_chatbot_api_no_message(self):
        response = self.app.post('/chatbot', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'response': 'No message provided.'})

    def test_chatbot_api_error(self):
        with patch('run.openai.ChatCompletion.create') as mock_chat_completion:
            mock_chat_completion.side_effect = Exception('OpenAI API error')
            response = self.app.post('/chatbot', json={'message': 'Hello'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'response': "Sorry, there was an error processing your request."})

    def test_404_error_page(self):
        response = self.app.get('/non-existent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.data)
        self.assertIn(b"The page you're looking for doesn't exist.", response.data)

    def test_500_error_page(self):
        # Simulate a server error by causing an exception in a route
        with patch('run.index') as mock_index:
            mock_index.side_effect = Exception('Server Error')
            response = self.app.get('/')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'500', response.data)
            self.assertIn(b'Sorry! Something went wrong on our end.', response.data)

if __name__ == '__main__':
    unittest.main()
