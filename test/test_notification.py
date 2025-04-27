import unittest
from datetime import datetime, timezone
import os

from app import create_app, db
from app.models import Notification
from app.services import NotificationService
from app.repositories import NotificationRepository

class NotificationTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.repo = NotificationRepository()
        self.service = NotificationService()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_notification(self, type_, message):
        return Notification(type=type_, message=message, date=datetime.now(timezone.utc))

    # models
    def test_model_creation(self):
        notification = self.create_notification('INFO', 'Test message')
        db.session.add(notification)
        db.session.commit()

        saved = Notification.query.first()
        self.assertIsNotNone(saved)
        self.assertEqual(saved.type, 'INFO')
        self.assertEqual(saved.message, 'Test message')

    # repositories
    def test_repo_save_and_find(self):
        n = self.create_notification('WARNING', 'From repo')
        self.repo.save(n)

        found = self.repo.find(n.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.message, 'From repo')

    def test_repo_find_all_and_find_by(self):
        self.repo.save(self.create_notification('INFO', 'One'))
        self.repo.save(self.create_notification('ERROR', 'Two'))
        self.repo.save(self.create_notification('WARNING', 'Three'))

        all_n = self.repo.find_all()
        self.assertEqual(len(all_n), 3)

        filtered = self.repo.find_by(type='ERROR')
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].type, 'ERROR')

    def test_repo_delete(self):
        n = self.create_notification('WARNING', 'To delete')
        self.repo.save(n)
        self.repo.delete(n)

        self.assertIsNone(self.repo.find(n.id))

    #  service
    def test_service_create_and_find(self):
        n = self.create_notification('INFO', 'Service info')
        created = self.service.create(n)

        found = self.service.find_by_id(created.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.message, 'Service info')

    def test_service_find_all(self):
        self.service.create(self.create_notification('INFO', 'Service 1'))
        self.service.create(self.create_notification('ERROR', 'Service 2'))

        all_n = self.service.find_all()
        self.assertEqual(len(all_n), 2)

    def test_service_delete(self):
        n = self.service.create(self.create_notification('ERROR', 'To be deleted'))
        self.service.delete(n.id)

        self.assertIsNone(self.service.find_by_id(n.id))


if __name__ == '__main__':
    unittest.main()
