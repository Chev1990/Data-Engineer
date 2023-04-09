import pymssql
import pyodbc
import pytest
import math

def connectdb():
    conndb = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};Server=(localdb)\\MyInstance;Database=TRN;integrated security=true')
    return conndb
"""
    AUTOTEST-001: [tablename] completeness
    Check that table tablename is not empty
    (for example,tablename in ("jobs", "employees"))
    Steps:
    0. Connect to the DB TRN
    1. Execute query: Count the number of rows in table(tablename) using count(*)
    Expected result: count of rows in table > 0, status: pass
"""
@pytest.mark.parametrize('tablename', ["jobs", "employees"])
def testempty(tablename):
    conn = connectdb()
    cur = conn.cursor()
    query = f"Select count(*) cnt from hr.{tablename}"
    cur.execute(query)
    row = cur.fetchall()
    conn.close()
    assert row[0][0] > 0, f'Table {tablename} is empty'
    #if row[0][0] > 50:
     #  print(f'Table {tablename} is not empty')
      # conn.close()
      # return 1
    #else:
     #   conn.close()
      #  str=f"Table {tablename} is empty"
      #  raise Exception(str)
"""
    AUTOTEST-002: [employees] validity
    Check for average salary of employees 
    Steps:
    0. Connect to the DB TRN
    1. Execute query: Calculate the average salary of employees using avg(*)
    Expected result: the average salary of employees = 8060, status: pass
"""
def testavgsalary():
    conn = connectdb()
    cur = conn.cursor()
    query = f"select avg(salary) from hr.employees"
    cur.execute(query)
    row = cur.fetchall()
    conn.close()
    assert row[0][0] == 8060, f'The average salary is not equal to 8060'
"""
    AUTOTEST-003: [departments] completeness
    Check for count the number of departments in table(departments)
    Steps:
    0. Connect to the DB TRN
    1. Execute query: Count the number of distinct department_name in table(departments) using count()
    Expected result: the number of distinct department_name = 11, status: pass
"""
def testcntkdepartments():
    conn = connectdb()
    cur = conn.cursor()
    query = f"select count(distinct department_name) from [hr].[departments]"
    cur.execute(query)
    row = cur.fetchall()
    conn.close()
    assert row[0][0] == 11, f'the number of distinct department_name is not equal to 11'
"""
    AUTOTEST-004: [jobs] uniqueness
    Check for duplicate rows in table jobs
    Steps:
    0. Connect to the DB TRN
    1. Execute query: Count the number of duplicate rows in jobs table
    Expected result: the number of duplicate rows equals 0, status: pass
"""
def testuniquenessjobs():
    conn = connectdb()
    cur = conn.cursor()
    query = f"select  job_id, job_title, min_salary,max_salary, count(*) cnt from hr.jobs group by job_id, job_title, min_salary,max_salary having count(*)>1"
    cur.execute(query)
    row = cur.fetchall()
    conn.close()
    assert len(row) == 0, f'there are the duplicate rows in jobs table'
"""
    AUTOTEST-005: [jobs] accuracy
    Check column value (min_salary) for specified job_title in Table Jobs
    (for examples,job_title = 'Public Accountant',min_salary=4200)
    Steps:
    0. Set a parameter min_salary according to specified job_title 
    1. Pass to function testminsalaryforjobtitle parameter, job_title from step 0 
    2. Connect to the DB TRN
    3. Execute query: check min_salary for specified job_title in Table Jobs 
    Expected result: min salary of specified job_title matchs the parameter of the function, status: pass
"""
@pytest.mark.parametrize('jobtitle', ["Public Accountant"])
@pytest.mark.parametrize('minsalary', [4200])
def testminsalaryforjobtitle(jobtitle, minsalary):
    conn = connectdb()
    cur = conn.cursor()
    query = f"select min_salary from hr.jobs where job_title = '{jobtitle}'"
    cur.execute(query)
    row = cur.fetchall()
    conn.close()
    assert row[0][0] == minsalary, f'min_salary is not equal to {minsalary} for job_title = {jobtitle} '

"""
    AUTOTEST-006: [employees] validity
    Check for max salary of employees 
    Steps:
    0. Connect to the DB TRN
    1. Execute query: Calculate the max salary of employees using max()
    Expected result: the max salary of employees = 24000, status: pass
"""

def testmaxsalaryofemployees():
    conn = connectdb()
    cur = conn.cursor()
    query = f"select max(salary) from hr.employees"
    cur.execute(query)
    row = cur.fetchall()
    conn.close()
    assert row[0][0] == 24000, f'max_salary of employees is not equal to 24000'

'''if __name__ == "__main__":
   # testemployees('employees')
    testempty('jobs')
    testavgsalary()
    testcntkdepartments()
    testuniquenessjobs()
    testminsalaryforjobtitle('Public Accountant', 4200)
    testmaxsalaryofemployees()'''