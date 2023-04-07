settings = [
    aws_region: "us-east-1",
    aws_credentials_id: "airflow-ec2-e2e-did",
    aws_admin_role_arn: "arn:aws:iam::123456789:role/dev-admin-role",
    aws_admin_credentials: "",
    aws_session_duration: "3600",
    iamPermissionsBoundaryARN: "arn:aws:iam::123456789:policy/user-internal-pb-hhe2e-2",
]
def gitId = 'jenkins-bitbucket'
def AWS_CRED_ID = 'ec2-e2e-did'

env.HTTP_PROXY = "http://webproxy.com:8080"
env.HTTPS_PROXY = "http://webproxy.com:8080"
def ROBOT_MODES = [
        'REGULAR_RUN'  : false,
        'REPORT_PORTAL_RUN': true
    ]

properties([
  parameters([
    gitParameter(
      branch: '',
      branchFilter: '.*',
      defaultValue: 'master',
      description: 'Repository branches',
      name: 'GIT_BRANCH',
      quickFilterEnabled: true,
      sortMode: 'NONE',
      tagFilter: '*',
      type: "PT_BRANCH",
      useRepository: "ssh://git@stash.com/hie/data-quality-serverless-framework.git"),
    string(
      name: 'TESTS_TAGS',
      defaultValue: '',
      description: '''Robot framework test tags for the run
      Help: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#tagging-test-cases''',
      trim: false
    ),
    string(
      name: "ROBOT_TESTS_FOLDER",
      defaultValue: 'robot/tests',
      description: '''Specify folder with RF tests to be executed.'''
    ),
    choice(
    name: "EXECUTION_MODE",
    choices: "${ROBOT_MODES.keySet().join('\n')}",
    defaultValue: 'REGULAR_RUN',
    description: 'Choose execution option for Robot framework run.'
    ),
    string(
      name: 'REPORT_PORTAL_UUID',
      defaultValue: '',
      description: '''API Key from Report portal
      Help: https://reportportal.io/docs/Edit-personal-information''',
      trim: false
    ),
    string(
      name: 'REPORT_PORTAL_URL',
      defaultValue: '',
      description: '''URL of deployed Report portal
      Ex.: http://internal-rp-webappal-123456789.us-east-1.elb.amazonaws.com''',
      trim: false
    ),
    string(
      name: 'REPORT_PORTAL_LAUNCH_NAME',
      defaultValue: '',
      description: '''Name of launch to display in Report portal
      Ex.: Data quality''',
      trim: false
    ),
    string(
      name: 'REPORT_PORTAL_PROJECT',
      defaultValue: '',
      description: '''Name of project in Report portal to put results to
      Ex.: superadmin_personal''',
      trim: false
    )
  ])
])

pipeline {
  agent {
    docker {
      image 'your-company.com/robot-tests-dq:current'
      args '-u 0:0 -v $WORKSPACE:/opt/at --shm-size "1568M"'
      reuseNode false
    }
  }

  stages {
      stage('Prepare parameters'){
            steps{
                script{
                   settings.aws_admin_credentials = readJSON file: '', text: (sts_assume_role(settings.aws_credentials_id, settings.aws_region, settings.aws_admin_role_arn, settings.aws_session_duration))
                }
            }
        }
    stage('Run automation testing '){
			   steps {
			       withEnv([
                        "AWS_ACCESS_KEY_ID=${settings.aws_admin_credentials[0]}",
                        "AWS_SECRET_ACCESS_KEY=${settings.aws_admin_credentials[1]}",
                        "AWS_SESSION_TOKEN=${settings.aws_admin_credentials[2]}",
                        "AWS_DEFAULT_REGION=${settings.aws_region}",
                    ]) {
			    script {
			        LISTENER = ""
                    if (params.EXECUTION_MODE == "REPORT_PORTAL_RUN") {
                        print('REPORT_PORTAL sync activated')
                        if (!params.REPORT_PORTAL_UUID) {
                            throw new Exception("REPORT_PORTAL_UUID has to be defined")
                        }
                        if (!params.REPORT_PORTAL_URL){
                            throw new Exception("REPORT_PORTAL_URL has to be defined")
                        }
                        if (!params.REPORT_PORTAL_LAUNCH_NAME){
                            throw new Exception("REPORT_PORTAL_LAUNCH_NAME has to be defined")
                        }
                        if (!params.REPORT_PORTAL_PROJECT){
                            throw new Exception("REPORT_PORTAL_PROJECT has to be defined")
                        }
                        LISTENER = "--listener robotframework_reportportal.listener \
                                    --variable RP_UUID:${params.REPORT_PORTAL_UUID} \
                                    --variable RP_ENDPOINT:${params.REPORT_PORTAL_URL} \
                                    --variable RP_LAUNCH:${params.REPORT_PORTAL_LAUNCH_NAME} \
                                    --variable RP_PROJECT:${params.REPORT_PORTAL_PROJECT}"
                    }

					sh """
						echo 'Start running Robot tests'
						robot $LISTENER -d $WORKSPACE/JOB_OUTPUT \
						${params.TESTS_TAGS} ${params.ROBOT_TESTS_FOLDER} || true
					"""
			    }
			   }
			}
  }}
  post {
    always {
      sh "echo 'Start generating Robot Framework report'"
         step([
             $class : 'RobotPublisher',
             outputPath : 'JOB_OUTPUT',
             outputFileName : "output.xml",
             disableArchiveOutput : true,
             passThreshold : 100,
             unstableThreshold: 95.0,
             onlyCritical : true,
             otherFiles : "*.png, *.txt",
         ])
    }
  }
}

def sts_assume_role(credentialsID, region, roleARN, sessionDuration){
    def aws_sts_credentials
    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID', credentialsId: "${credentialsID}", secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
        aws_sts_credentials = sh (returnStdout: true, script: "aws sts assume-role --role-arn ${roleARN} --role-session-name jenkins-airflow-e2e-${BUILD_NUMBER} --output json --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' --duration-seconds ${sessionDuration}").trim()
    }
    return aws_sts_credentials
}