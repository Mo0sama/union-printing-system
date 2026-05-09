from django.test import TestCase

from .models import CompanySetting


class CompanySettingTests(TestCase):
    def test_get_settings_creates_default(self):
        s = CompanySetting.get_settings()
        self.assertIsNotNone(s)
        self.assertEqual(s.company_name, 'UNION FOR DIGITAL PRINTING')

    def test_get_settings_returns_same_instance(self):
        s1 = CompanySetting.get_settings()
        s2 = CompanySetting.get_settings()
        self.assertEqual(s1.pk, s2.pk)
