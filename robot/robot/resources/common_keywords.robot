*** Settings ***
Documentation   Common Setup and Teardown keywords

Resource  variables.robot

*** Variables ***
${AWS_SF_MAX_RUNNING_TIMEOUT}        400  #sec
${AWS_SF_MAX_AWAIT_RUNNING_TIMEOUT}  60   #sec

*** Keywords ***
Verify constraints
    [Arguments]  ${check}
    [Documentation]  Logs errors if any for each constraint.
    ${error} =  convert to string  ${check['error']}
    IF  '${error}' != ''
        fail  Constraint ${check['check_name']} failed with error: ${error}
    END

Select DQ results from Athena for the table
    [Arguments]  ${table_name}
    [Documentation]  Calls AWS Athena for query results by boto3 client.

    ${TABLE_CHECKS_SQL} =  evaluate  "${TABLE_CHECKS_SQL}".format('\"constraint\", \"constraint_message\"', '${CURRENT_YEAR}', '${CURRENT_MONTH}', '${table_name}')
    Log  ${TABLE_CHECKS_SQL}

    ${resp} =  start_query_execution  ${TABLE_CHECKS_SQL}  ${ATHENA_RESULTS_LOCATION}
    ${data} =  wait until keyword succeeds  10 sec  3 sec  get_query_results   ${resp['QueryExecutionId']}
    log  ${data}

    ${rows_results} =  Set Variable  ${data['ResultSet']['Rows'][1::]}
    log  ${rows_results}

    ${checks_dict} =  construct_dq_check_response  ${rows_results}
    log  ${checks_dict}
    set test variable  ${DQ_CONSTRAINTS_RESULTS}  ${checks_dict}

Invoke step function with json input
    [Arguments]  ${json_input}  ${sf_name}=data-quality-sm
    [Documentation]  Invoke step function using json as input.

    ${dict_input} =  make_dict_from_json_file  ${json_input}
    ${str_input} =  evaluate  json.dumps(${dict_input})

    ${datetime} =  Get Current Date  result_format=datetime
    Set suite variable  ${CURRENT_YEAR}   ${datetime.year}
    ${month_with_leading_zero} =  evaluate  '${datetime.month}'.zfill(2)
    Set suite variable  ${CURRENT_MONTH}  ${month_with_leading_zero}

    Invoke lambda or step function  step  ${sf_name}  ${str_input}

Invoke lambda or step function
    [Arguments]  ${function_type}  ${function_name}  ${input}=${None}
    [Documentation]  Deploy lambda or step function (function arg should be "lambda" or "step").

    ${response}=  run keyword  invoke ${function_type} function  ${function_name}  ${input}
    ${wait_func_name}=  set variable if  "${function_type}" == "step"  ${response}  ${function_name}
    wait until lambda or step function finished  ${function_type}  ${wait_func_name}

Wait until lambda or step function finished
    [Arguments]  ${function}  ${wait_func_name}
    [Documentation]  Wait until step or lambda function ${wait_func_name}
                     ...  finished and verify result status.

    wait until keyword succeeds  ${AWS_SF_MAX_AWAIT_RUNNING_TIMEOUT} sec  3 sec
    ...  ${function} function is running  ${wait_func_name}
    wait until keyword succeeds  ${AWS_SF_MAX_RUNNING_TIMEOUT} sec  30 sec
    ...  ${function} function finished successfully  ${wait_func_name}
