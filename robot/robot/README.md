# Environment setup

## Create virtual environment for tests execution
```bash
cd robot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd resources/libraries && python setup.py install
```

## Deploy and configure Data Quality solution
Follow [instructions](../README.md)

## Run robot tests
```bash
robot tests/robot/tests/legislators_db_tests.robot
```

# Report portal integration with Robot Framework
For the integration library [robotframework-reportportal](https://github.com/reportportal/agent-Python-RobotFramework)
is used. This is an officially supported library for RF from report portal community.

To implement the integration you will need to add `robotframework-reportportal` dependency to your RF project and 
add some commands to the script of starting your test cases.

## Run RF tests execution with Report portal integration
If you start RF tests with `robot` in one thread (RP_LAUNCH on Report portal side will be created automatically)
please run as below:
```
robot --listener robotframework_reportportal.listener \
        --variable RP_UUID:4d51158b-2b49-4036-92e1-384ef48e1536 \
        --variable RP_ENDPOINT:http://10.118.195.189:8080 \
        --variable RP_LAUNCH:PQA_DAILY \
        --variable RP_PROJECT:superadmin_personal \
        --variable RP_ATTACH_REPORT:True \
        robot/tests/legislators_db_tests.robot
```
