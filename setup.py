import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/scheduled-job-manager>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'scheduled_job_manager/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = "https://github.com/uw-it-aca/scheduled-job-manager"
setup(
    name='scheduled-job-manager',
    version=VERSION,
    packages=['scheduled_job_manager'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=[
        'Django<1.11',
        'boto3',
        'simplejson',
        'django-compressor',
        'django-userservice==1.2.1',
        'pytz',
        'UW-Django-SAML2>=0.4.5,<1.0',
        'django-aws-message>=1.0.1,<1.1',
        'Django-SupportTools>=2.0.4,<3.0',
        'django_client_logger',
    ],
    license='Apache License, Version 2.0',
    description=('App to centrally mangage scheduled jobs in a distributed environment'),
    long_description=README,
    url=url,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
