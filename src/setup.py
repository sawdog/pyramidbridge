import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = [
    'arrow',
    'PyYAML',
    'pymlconf==1.0.1',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_services',
    'pyramid_debugtoolbar',
    'python-dateutil',
    'rethinkdb',
    'waitress',
    'WebOb',
    ]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov',
    ]

setup(name='pyramidbridge',
      version='0.1',
      description='pyramid bridge, routing POSTs to configurable backends',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Andrew Sawyers',
      author_email='andrew.sawyers@sawdog.com',
      keywords='web pyramid pylons rethinkDB bridge SmartThings',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = pyramidbridge:main
      """,
      )
