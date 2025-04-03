import os
import shutil
from datetime import datetime
import sys

# Define the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Check if backup is needed (default: no backup)
create_backup = False
if len(sys.argv) > 1 and sys.argv[1].lower() == '--backup':
    create_backup = True

# Define the apps that might have migrations
apps = ['core', 'AuthApp']

if create_backup:
    # Create a backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(base_dir, f"migrations_backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Creating backup in: {backup_dir}")

for app in apps:
    migrations_dir = os.path.join(base_dir, app, 'migrations')
    
    # Skip if the directory doesn't exist
    if not os.path.exists(migrations_dir):
        print(f"No migrations directory found for app: {app}")
        continue
    
    if create_backup:
        # Create a backup of the entire migrations directory
        app_backup_dir = os.path.join(backup_dir, app)
        os.makedirs(app_backup_dir, exist_ok=True)
        
        # Copy all migration files to backup
        for filename in os.listdir(migrations_dir):
            if filename.endswith('.py'):
                source_file = os.path.join(migrations_dir, filename)
                dest_file = os.path.join(app_backup_dir, filename)
                shutil.copy2(source_file, dest_file)
                print(f"Backed up: {source_file} to {dest_file}")
    
    # Remove migration files except __init__.py
    migration_count = 0
    for filename in os.listdir(migrations_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            file_path = os.path.join(migrations_dir, filename)
            os.remove(file_path)
            print(f"Removed: {file_path}")
            migration_count += 1
    
    print(f"Removed {migration_count} migration files from {app}")

print("\nMigration files have been successfully removed while preserving __init__.py files.")
print("\nIMPORTANT: If you need to recreate migrations, run:")
print("python manage.py makemigrations")
print("python manage.py migrate --fake-initial")
