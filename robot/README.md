# Description of project
Project Robot framework(RF) is automated test cases for checking of data in following tables: jobs,employees,departments.

## Environment
### Test Automation Framework
This project uses the Robot framework,pyodbc,pymssql drivers and MS SQL DB.
### Create virtual environment for tests execution
Installing dependencies:
```bash
pip install -r requirements.txt
pip install robotframework
```
Run the tests and generate a HTML report
In the Output folder you will find reports with test details log.html and report.html.
```bash
robot -d Output robot_test.robot
```

