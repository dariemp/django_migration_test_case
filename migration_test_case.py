"""
Useful test case for testing migrations
Inspired by:
    - https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    - https://github.com/plumdog/django_migration_testcase
"""
from django.test import TestCase
from django.core.management import call_command


class MigrationTestCase(TestCase):
    """
    Test case to inherit from for testing migrations
    """
    app_name = None
    migrate_from = None
    migrate_to = None
    database = None

    def setUp(self):
        assert self.app_name, \
            "TestCase '{}' must define 'app_name' property".format(type(self).__name__)
        assert self.migrate_from, \
            "TestCase '{}' must define 'migrate_from' property".format(type(self).__name__)
        assert self.migrate_to, \
            "TestCase '{}' must define  'migrate_to' property".format(type(self).__name__)
        self._migration_run = True
        self.run_backward_migration()

    def tearDown(self):
        call_command('migrate', self.app_name, **self.command_kwargs())

    def get_model_before(self, model_name):
        if self._migration_run:
            raise RuntimeError('Migration already run, please run the backward migration')
        from django.apps import apps
        return apps.get_model(self.app_name, model_name)

    def get_model_after(self, model_name):
        if not self._migration_run:
            raise RuntimeError('Migration not run, please run the forward migration')
        from django.apps import apps
        return apps.get_model(self.app_name, model_name)

    def run_forward_migration(self):
        if self._migration_run:
            raise RuntimeError('Forward migration already run')
        self._migrate(self.migrate_to)
        self._migration_run = True

    def run_backward_migration(self):
        if not self._migration_run:
            raise RuntimeError('Forward migration not run')
        self._migrate(self.migrate_from)
        self._migration_run = False

    def command_kwargs(self):
        kwargs = {
            'verbosity': 0
        }
        if self.database:
            kwargs['database'] = self.database
        return kwargs

    def _migrate(self, migration_name):
        call_command('migrate', self.app_name, migration_name, **self.command_kwargs())
