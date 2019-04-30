from django.core.management import call_command
from django.apps import apps
from django.db.models import Q
import datetime

from autoproofreader.tests.common import AutoproofreaderTestCase
from autoproofreader.models import AutoproofreaderResult


class CommandsTests(AutoproofreaderTestCase):
    def assert_db_population_state(self, should_exist):
        assertion = self.assertTrue if should_exist else self.assertFalse
        for proofreader_model in apps.get_app_config("autoproofreader").get_models():
            assertion(proofreader_model.objects.all().exists())

    def test_reset_floodfilling(self):
        self.assert_db_population_state(True)
        call_command("reset_autoproofreader", "-y")
        self.assert_db_population_state(False)

    def test_remove_old_results(self):
        AutoproofreaderResult(
            name="test_recent",
            status="complete",
            config_id=1,
            skeleton=1,
            skeleton_csv="None",
            model=1,
            private=False,
            permanent=False,
            errors="None",
            creation_time=datetime.datetime.now(),
            edition_time=datetime.datetime.now(),
            user_id=3,
            project_id=3,
        ).save()
        AutoproofreaderResult(
            name="test_old_permanent",
            status="complete",
            config_id=2,
            skeleton=2,
            skeleton_csv="None",
            model=2,
            private=False,
            permanent=True,
            errors="None",
            creation_time=datetime.datetime.now() - datetime.delta(days=7),
            edition_time=datetime.datetime.now() - datetime.delta(days=7),
            user_id=3,
            project_id=3,
        ).save()
        old = Q(
            completion_time__lt=datetime.datetime.now() - datetime.timedelta(days=1)
        )
        self.assertEqual(
            len(AutoproofreaderResult.objects.filter(old & Q(permanent=False))), 2
        )
        self.assertEqual(len(AutoproofreaderResult.objects.all()), 4)
        call_command("clear_old_results", "-y")
        self.assertEqual(
            len(AutoproofreaderResult.objects.filter(old & Q(permanent=False))), 0
        )
        self.assertEqual(len(AutoproofreaderResult.objects.all()), 2)
