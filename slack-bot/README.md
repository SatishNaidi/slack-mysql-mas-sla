### Slack to Jenkins Bot ###
Bot is developed in python, will be running the jobs based on the user input in slack channel
    -get all available jobs in Jenkings type get-all-jobs
    -You can run a jenkins job by asking run:<jobname>
    -You can run a jenkins job with parameters by asking run:<jobname>,key1:value1,key2:value2
    -To get the status of job-status:<jobname>

###Dependencies
Slack Secretes are stored as Env Variables
    -SLACK_BOT_TOKEN="417761718486417761718486417761718486417761718486"
    -USER_VALIDATION_TOKEN="xoxp-417761718486-416568558261-c3dff4f8f9bab3137eda6c1f963622ab"

Should have a Properties/config.cfg file to hold the configuration related Jenkins

Sample config.cfg
[Jenkins]
JENKINS_URL=http://ec2-58-34-249-217.ap-south-1.compute.amazonaws.com:8080

[usermappings]
user1=1156ab74dee882d3a87fa497c4790fd4
user2=114c9f6adf0c3ac92b7a071efd3d988
