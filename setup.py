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
        'Django>=2.1.1,<3.0',
        'boto3',
        'simplejson',
        'django-compressor',
        'django-userservice>=3.1,<4.0',
        'django-user-agents',
        'django-pyscss',
        'pytz',
        'UW-Django-SAML2>=1.0,<2.0',
        'django-aws-message>=1.2.3,<2.0',
        'Django-SupportTools>=3.1.1,<4.0',
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
