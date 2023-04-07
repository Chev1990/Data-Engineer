import time
import os
from robot.api.deco import library, keyword

import boto3

REGION = 'us-east-1'  #TODO os.getenv('AWS_REGION')


@library(scope='GLOBAL', auto_keywords=True)
class StepFunctionHelper:

    def __init__(self):
        self.__sf_client = boto3.client('stepfunctions', REGION)

    @keyword
    def get_current_step_functions_names(self):
        response = self.get_current_step_functions_info()
        return [sm['name'] for sm in response['stateMachines']]

    @keyword
    def get_current_step_functions_info(self):
        return self.__sf_client.list_state_machines(maxResults=50)

    @keyword
    def get_step_function_arn_by_name(self, sf_name):
        sf_info = self.get_current_step_functions_info()
        sf_arn = [sm['stateMachineArn'] for sm in sf_info['stateMachines'] if sm['name'] == sf_name]
        return sf_arn[0]

    @keyword
    def get_step_function_executions(self, sf_name):
        sf_arn = self.get_step_function_arn_by_name(sf_name)
        response = self.__sf_client.list_executions(stateMachineArn=sf_arn, maxResults=50,)
        return [function['name'] for function in response['executions']]

    @keyword
    def get_step_function_definition_resources(self, sf_name):
        sf_arn = self.get_step_function_arn_by_name(sf_name)
        return self.__sf_client.describe_state_machine(stateMachineArn=sf_arn)["definition"]

    @keyword
    def invoke_step_function(self, sf_name, state_machine_input=None):
        millis = int(round(time.time() * 1000))
        sf_arn = self.get_step_function_arn_by_name(sf_name)

        response = self.__sf_client.start_execution(
            stateMachineArn=sf_arn,
            name=f'Autotest_run_{millis}',
            input=state_machine_input
        )
        return response['executionArn']

    @keyword
    def step_function_is_running(self, sf_arn):
        response = self.__sf_client.describe_execution(
            executionArn=sf_arn
        )
        print(response)
        if response['status'] == "RUNNING":
            print(f'Step function {sf_arn} is running!')
        else:
            raise Exception(f"Step function {sf_arn} is not running")

    @keyword
    def step_function_finished_successfully(self, sf_arn):
        response = self.__sf_client.describe_execution(
            executionArn=sf_arn
        )
        print(response)
        if response['status'] == "SUCCEEDED":
            print(f'Step function {sf_arn} finished successfully!')
        else:
            raise Exception(f"Step function {sf_arn} not succeeded")


@library(scope='GLOBAL', auto_keywords=True)
class AthenaHelper:

    INTERMEDIATE_STATES = (
        'QUEUED',
        'RUNNING',
    )
    FAILURE_STATES = (
        'FAILED',
        'CANCELLED',
    )

    def __init__(self):
        self.__client = boto3.client('athena', REGION)

    @keyword
    def start_query_execution(self, query_string, output_location):
        response = self.__client.start_query_execution(
            QueryString=f"{query_string}",
            ResultConfiguration={
                'OutputLocation': output_location,
            },
        )
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception('Athena request response code != 200 OK')
        return response

    @keyword
    def get_query_results(self, query_execution_id, next_token_id=None, max_results=100):
        query_state = self._check_query_status(query_execution_id)
        if query_state is None:
            raise Exception('Invalid Query state')
        elif query_state in self.INTERMEDIATE_STATES or query_state in self.FAILURE_STATES:
            raise Exception(f'Query is in {query_state} state. Cannot fetch results')
        result_params = {'QueryExecutionId': query_execution_id, 'MaxResults': max_results}
        if next_token_id:
            result_params['NextToken'] = next_token_id
        return self.__client.get_query_results(**result_params)

    def _check_query_status(self, query_execution_id):
        """
        Fetch the status of submitted athena query. Returns None or one of valid query states.

        :param query_execution_id: Id of submitted athena query
        :type query_execution_id: str
        :return: str
        """
        response = self.__client.get_query_execution(QueryExecutionId=query_execution_id)
        state = None
        try:
            state = response['QueryExecution']['Status']['State']
        except Exception as ex:
            print('Exception while getting query state %s', ex)
        finally:
            return state
