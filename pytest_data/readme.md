# Description of project
Project python Pytest is automated test cases for checking of data in following tables: jobs,employees,departments.

## Environment
### Test Automation Framework
This project uses the pytest framework,pyodbc,pymssql drivers and MS SQL DB.
### Create virtual environment for tests execution
Use the driver list and pytest version from requirements.txt. to run tests.
```bash
pip install -r requirements.txt
```
### Report
To generate a HTML report for tests, we have to install a plugin with the command
```bash
pip install pytest-html
```
Execute of tests
```bash
python venv/test_data.py
pytest -v -s venv/ --html=report.html
pytest venv/ --html-report=./report --title='PYTEST REPORT'
```

