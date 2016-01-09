BackupProfiler
=======

### Step 1: Run Application
    sudo python manage.py runserver
    
### Step 2: Application finds location of backups

### Step 3: User selects backups to extract from homepage

### Step 4: Application uses iosRecovery.py script to extract data from backup

### Step 5: Once all data is extracted, user can use the web application to sift through information

#### Dependencies

Pillow 2.1.0  https://pypi.python.org/pypi/Pillow/2.1.0

    pip install Pillow

Django 1.7+ https://docs.djangoproject.com/en/1.8/howto/windows/

    pip install django

Plistlib https://docs.python.org/2.7/library/plistlib.html

Biplist https://pypi.python.org/pypi/biplist/0.2

Geocoder http://geocoder.readthedocs.org/api.html#install

    pip install geocoder

