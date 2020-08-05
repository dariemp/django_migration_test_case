"""Useful test case for testing migrations Inspired by:

- https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
- https://github.com/plumdog/django_migration_testcase
"""
from django.core import management
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.test import TransactionTestCase


class MigrationTestCase(TransactionTestCase):
    """Test case to inherit from for testing migrations."""

    app_name = None
    migrate_from = None
    migrate_to = None
    database = None

    def setUp(self):
        """Setup the migration test case by migrating back the migration
        specified in `migrate_from`."""
        assert self.app_name, "TestCase '{}' must define 'app_name' property".format(
            type(self).__name__
        )
        assert (
            self.migrate_from
        ), "TestCase '{}' must define 'migrate_from' property".format(
            type(self).__name__
        )
        assert (
            self.migrate_to
        ), "TestCase '{}' must define  'migrate_to' property".format(
            type(self).__name__
        )
        self._migration_run = True
        self._apps = None
        self.run_backward_migration()

    def tearDown(self):
        """Finalize migration test case by applying all available
        migrations."""
        management.call_command("migrate", self.app_name, **self.command_kwargs())

    def get_model_before(self, model_name):
        """Get model before applying any migration."""
        if self._migration_run:
            raise RuntimeError(
                "Migration already run, please run the backward migration"
            )
        return self._apps.get_model(self.app_name, model_name)

    def get_model_after(self, model_name):
        """Get model after applying migration specified in `migrate_from`."""
        if not self._migration_run:
            raise RuntimeError("Migration not run, please run the forward migration")
        return self._apps.get_model(self.app_name, model_name)

    def run_forward_migration(self):
        """Run/apply migrations from `migrate_from` to `migrate_to`."""
        if self._migration_run:
            raise RuntimeError("Forward migration already run")
        loader = MigrationLoader(connection)
        self._migrate(self.migrate_to)
        self._apps = loader.project_state([(self.app_name, self.migrate_to)]).apps
        self._migration_run = True

    def run_backward_migration(self):
        """Run/unapply migrations from `migrate_to` to `migrate_from`."""
        if not self._migration_run:
            raise RuntimeError("Forward migration not run")
        loader = MigrationLoader(connection)
        self._migrate(self.migrate_from)
        self._apps = loader.project_state([(self.app_name, self.migrate_from)]).apps
        self._migration_run = False

    def command_kwargs(self):
        """Pass more arguments to the migrate command line."""
        kwargs = {"verbosity": 0}
        if self.database:
            kwargs["database"] = self.database
        return kwargs

    def _migrate(self, migration_name):
        """Run the migrate command."""
        management.call_command(
            "migrate", self.app_name, migration_name, **self.command_kwargs()
        )
