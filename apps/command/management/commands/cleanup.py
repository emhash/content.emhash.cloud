import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.conf import settings
from django.db import connection

"""
Usage:
    python manage.py cleanup
    python manage.py cleanup --reset-db
    python manage.py cleanup --apps accounts forms tracking

Guide:
python manage.py cleanup                    # Clean all apps
python manage.py cleanup --apps accounts   # Clean specific apps
python manage.py cleanup --force           # Skip confirmations
python manage.py cleanup --reset-db        # Reset database
"""

class Command(BaseCommand):
    help = 'Clean up migration files and clear cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apps',
            nargs='+',
            help='Specific apps to clean (default: all apps)',
            default=[]
        )
        parser.add_argument(
            '--reset-db',
            action='store_true',
            help='Reset database (WARNING: This will delete all data!)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompts',
        )
        parser.add_argument(
            '--keep-migrations',
            action='store_true',
            help='Keep migration files, only clear cache',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧹 Starting cleanup process...\n')
        )

        # Get apps to clean
        apps_to_clean = self.get_apps_to_clean(options['apps'])
        
        # Clear cache
        self.clear_cache()
        
        # Clear Python cache files
        self.clear_python_cache()
        
        # Delete migration files (if not keeping them)
        if not options['keep_migrations']:
            self.delete_migration_files(apps_to_clean, options['force'])
        
        # Reset database (if requested)
        if options['reset_db']:
            self.reset_database(options['force'])
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Cleanup completed successfully!')
        )

    def get_apps_to_clean(self, specified_apps):
        """Get list of apps to clean."""
        if specified_apps:
            return specified_apps
        
        # Get all installed apps
        installed_apps = []
        for app in settings.INSTALLED_APPS:
            if app.startswith('apps.'):
                app_name = app.split('.')[-1]
                installed_apps.append(app_name)
        
        return installed_apps

    def clear_cache(self):
        """Clear Django cache."""
        try:
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('✅ Django cache cleared')
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Could not clear cache: {e}')
            )

    def clear_python_cache(self):
        """Clear Python __pycache__ directories."""
        cleared_count = 0
        
        # Clear project root __pycache__
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    pycache_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(pycache_path)
                        cleared_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Could not remove {pycache_path}: {e}')
                        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Cleared {cleared_count} __pycache__ directories')
        )

    def delete_migration_files(self, apps_to_clean, force=False):
        """Delete migration files from specified apps."""
        deleted_count = 0
        
        for app_name in apps_to_clean:
            migrations_path = f'apps/{app_name}/migrations'
            
            if not os.path.exists(migrations_path):
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Migrations directory not found: {migrations_path}')
                )
                continue
            
            # Get all migration files (excluding __init__.py)
            migration_files = []
            for file in os.listdir(migrations_path):
                if file.endswith('.py') and file != '__init__.py':
                    migration_files.append(file)
            
            if not migration_files:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  No migration files found in {migrations_path}')
                )
                continue
            
            # Confirm deletion
            if not force:
                self.stdout.write(f'\n📁 Found {len(migration_files)} migration files in {migrations_path}:')
                for file in migration_files:
                    self.stdout.write(f'   - {file}')
                
                confirm = input(f'\n❓ Delete these migration files? (y/N): ')
                if confirm.lower() != 'y':
                    self.stdout.write(
                        self.style.WARNING(f'⏭️  Skipping {migrations_path}')
                    )
                    continue
            
            # Delete migration files
            for file in migration_files:
                file_path = os.path.join(migrations_path, file)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    self.stdout.write(f'🗑️  Deleted: {file_path}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Could not delete {file_path}: {e}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Deleted {deleted_count} migration files')
        )

    def reset_database(self, force=False):
        """Reset database (WARNING: This deletes all data!)."""
        if not force:
            self.stdout.write(
                self.style.ERROR('\n⚠️  WARNING: This will delete ALL data in the database!')
            )
            confirm = input('❓ Are you sure you want to reset the database? (yes/NO): ')
            if confirm.lower() != 'yes':
                self.stdout.write(
                    self.style.WARNING('⏭️  Database reset cancelled')
                )
                return
        
        try:
            # Drop all tables
            with connection.cursor() as cursor:
                cursor.execute("DROP SCHEMA public CASCADE;")
                cursor.execute("CREATE SCHEMA public;")
                cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
                cursor.execute("GRANT ALL ON SCHEMA public TO public;")
            
            self.stdout.write(
                self.style.SUCCESS('✅ Database reset completed')
            )
            self.stdout.write(
                self.style.WARNING('💡 Run "python manage.py migrate" to recreate tables')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Could not reset database: {e}')
            )
