*** Settings ***
Library           DatabaseLibrary
Library           OperatingSystem
Library  String
Suite Setup     Connect To Database Using Custom Params   pyodbc   ${DBHost_ConnectionString}
Suite Teardown  Disconnect From Database

*** Variables ***
${DBHost_ConnectionString}    'DRIVER={ODBC Driver 17 for SQL Server};Server=(localdb)\\MyInstance;Database=TRN;integrated security=true'
*** Test Cases ***
Test 1. Employees: Verify Query - Row Count employees table
    [Tags]    AUTOTEST-001: []
    [documentation]
    ...  *Test Steps:*
    ...  1. Connect to DB;
    ...  2. Execute query: Count the number of rows in table('employees') using count(*)
    ...
    ...  *Expected result:* the count of rows in table 'employees' equals 40
    ${output} =    Query    SELECT COUNT(*) FROM hr.employees;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [(40, )]
Test 2. Departments: Verify a Table Exists
    [Tags]  AUTOTEST-002: []
    [documentation]
    ...  *Test Steps:*
    ...  1. Connect to DB;
    ...  2. Execute query: Check the table('departments') is in this DB
    ...
    ...   *Expected result:* the table 'departments' exists in DB
    Table Must Exist  departments
Test 3. Employees: Verify the average salary of employees is equal to a specified value
    [Tags]  AUTOTEST-003: []
    [documentation]
    ...  *Test Steps:*
    ...  1. Connect to DB;
    ...  2. Execute query: Calculate the average salary of employees using avg(*)
    ...
    ...   *Expected result:* the average salary of employees = 8060
    ${output} =    Query    select left(avg(salary),4) from hr.employees;
    Log    ${output}
    Should Be Equal As Strings    ${output}    [('8060', )]
Test 4. Jobs: Verify duplicate rows are not in table jobs
    [Tags]  AUTOTEST-004: []
    [documentation]
    ...  *Test Steps:*
    ...  1. Connect to DB;
    ...  2. Execute query: Count the number of duplicate rows in jobs table
    ...
    ...   *Expected result:* count of rows in table > 0
    ${output} =    Query   select job_id, job_title, min_salary,max_salary, count(*) cnt from hr.jobs group by job_id, job_title, min_salary,max_salary having count(*)>1;
    Log    ${output}
    Should Be Equal As Strings    ${output}    []
Test 5. Jobs: Check column value (min_salary) for job_title = 'Public Accountant'
    [Tags]  AUTOTEST-005: []
    [documentation]
    ...  *Test Steps:*
    ...  1. Connect to DB;
    ...  2. Execute query: min_salary for specified job_title
    ...
    ...   *Expected result:* min salary of specified job_title is equal to 4200
    ${output} =    Query   select left(min_salary,4) from hr.jobs where job_title = 'Public Accountant';
    Log    ${output}
    Should Be Equal As Strings    ${output}    [('4200', )]
Test 6. Regions: Check If Exists In DB - region Europe
    [Tags]  AUTOTEST-006: []
    [documentation]
    ...  *Test Steps:*
    ...  1. Connect to DB;
    ...  2. Execute query: check thst region Europe Exists In DB
    ...
    ...   *Expected result:* region Europe Exists In DB with id = 1
    Check If Exists In Database    SELECT region_id FROM hr.regions WHERE region_name = 'Europe';