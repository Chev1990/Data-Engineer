*** Settings ***
Library  Screenshot
*** Variables ***
${NAME}  John
*** Test Cases ***
Screenshot and Log Test Case
   Take Screenshot and Log Text  ${NAME}
*** Keywords ***
Take Screenshot and Log Text
   [Arguments]  ${NAME}
   Take Screenshot
   Log  The screenshot was taken by ${NAME}...
