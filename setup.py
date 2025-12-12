from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install as _install


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        import db_report
        db_report.copy_config()


class PostInstallCommand(_install):
    """Post-installation for installation mode."""
    def run(self):
        _install.run(self)
        import db_report
        db_report.copy_config()


setup(name='db_report',
      version='0.0.11',
      packages=['db_report', 'db_report.config', 'db_report.utils', 'db_report.formats'],
      url='https://github.com/oleglpts/reporter',
      license='MIT',
      platforms='any',
      author='Oleg Lupats',
      author_email='oleglupats@gmail.com',
      description='Database report generation',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      zip_safe=False,
      classifiers=[
            'Operating System :: POSIX',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5'
      ],
      entry_points={
          'console_scripts': [
              'db_report = db_report.__main__:main'
          ]
      },
      python_requires='>=3',
      package_data={
          'db_report': [
              'data/*',
              'data/locale/ru/LC_MESSAGES/*',
              'data/locale/en/LC_MESSAGES/*',
              'data/reports/*',
              'data/test/*',
              'test/*'
          ]
      },
      include_package_data=True,
      install_requires=[
          'xls-report>=0.0.5',
          'bottle>=0.12.17',
          'pyodbc>=4.0.26',
          'pycurl>=7.43.0.3',
          'psycopg2-binary>=2.9.1'
      ],
      cmdclass={
          'develop': PostDevelopCommand,
          'install': PostInstallCommand,
      })
