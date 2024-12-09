# ODBC fake data generator
This repository contains script for generating fake Department and Employee tables and inserting them into ODBC-connected database.
## Requirements
- [Faker](https://pypi.org/project/Faker/)
- [pyodbc](https://pypi.org/project/pyodbc/)

By default, script requires Microsoft SQL Server stack:
- T-SQL.
- ODBC Driver 18 for SQL Server.
- Automatic instance of Microsoft SQL Server LocalBD `(localdb)\MSSQLLocalDB`.

Script was tested on Python 3.11 with SQL Server Express 2019 LocalDB from Visual Studio Installer.