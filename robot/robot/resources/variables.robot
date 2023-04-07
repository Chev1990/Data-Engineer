*** Settings ***
Documentation   Robot resources and variables for all tests

Library   String
Library   OperatingSystem
Library   requests
Library   DateTime
Library   Collections

Library   Utils
Library   AwsServices.StepFunctionHelper
Library   AwsServices.AthenaHelper


Resource  ./common_keywords.robot

*** Variables ***
#${AWS_REGION}                    %{AWS_REGION=us-east-1}

${DQ_RESULTS_DB}                 data_quality_db
${DQ_CONSTRAINTS_RESULTS_TABLE}  constraints_verification_results

${ATHENA_RESULTS_LOCATION}    s3://athena-bucket-dq/playground/
${TABLE_CHECKS_SQL}           SELECT {} FROM ${DQ_RESULTS_DB}.${DQ_CONSTRAINTS_RESULTS_TABLE}
                              ...  WHERE year='{}' AND month='{}' AND \\"table\\" = '{}';

${GLUE_LEGISLATORS_DB}             legislators
${GLUE_LEGISLATORS_PERSONS}        persons_json
${GLUE_LEGISLATORS_ORGANIZATIONS}  organizations_json

