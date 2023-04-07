*** Settings ***
Documentation  Contains Data Quality constraints checks for legislators DB in AWS Glue.

Resource   ../resources/variables.robot

Force Tags      legislators

Suite Setup     Invoke step function with json input  robot/resources/jsons/sf_input.json
Test Template   Verify constraints

*** Test Cases ***
Persons_json table has DQ constraints values as expected
    [Tags]  AUTO-306
    [Documentation]
    ...  | *Setup:*
    ...  | 0. Setup legislators DB with persons_json table in AWS Glue.
    ...  | 1. Trigger Step function with legislators.persons_json table and await run finish.
    ...  |
    ...  | *Test Steps:*
    ...  | 2. Query DQ constraints results from AWS Athena by API\CLI.
    ...  |
    ...  | *Expected result:*
    ...  | 0. Legislators DB with persons_json table are present in AWS Glue.
    ...  | 1. Step function finished successfully.
    ...  | 2. Persons table DQ constraints were calculated as expected.
    [Setup]  Select DQ results from Athena for the table  ${GLUE_LEGISLATORS_PERSONS}
    FOR  ${constraint}  IN  @{DQ_CONSTRAINTS_RESULTS}
         ${constraint}
    END

Organizations_json table has DQ constraints values as expected
    [Tags]  AUTO-306
    [Documentation]
    ...  | *Setup:*
    ...  | 0. Setup legislators DB with organizations_json table in AWS Glue.
    ...  | 1. Trigger Step function with legislators.organizations_json table and await run finish.
    ...  |
    ...  | *Test Steps:*
    ...  | 2. Query DQ constraints results from AWS Athena by API\CLI.
    ...  |
    ...  | *Expected result:*
    ...  | 0. Legislators DB with organizations_json table are present in AWS Glue.
    ...  | 1. Step function finished successfully.
    ...  | 2. Organizations table DQ constraints were calculated as expected.
    [Setup]  Select DQ results from Athena for the table  ${GLUE_LEGISLATORS_ORGANIZATIONS}
    FOR  ${constraint}  IN  @{DQ_CONSTRAINTS_RESULTS}
         ${constraint}
    END
