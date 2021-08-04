from setuptools import setup
from setuptools import find_packages

version = '0.1.0'

with open('README.md') as f:
    readme = f.read()

setup(
    name='certbot-cpanel',
    version=version,
    description='certbot plugin to allow acme dns-01 authentication name and certificate installation in a cPanel.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/0x3333/certbot-cpanel',
    author='Tercio Filho',
    author_email='terciofilho@gmail.com',
    license='Apache Licence 2.0',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    keywords='certbot letsencrypt cpanel dns-01 installer plugin',
    install_requires=[
        'certbot',
        'zope.interface',
    ],
    entry_points={
        'certbot.plugins': [
            'auth = certbot_cpanel.dns:Authenticator',
            'install = certbot_cpanel.installer:Installer',
        ],
    },
)
