import os
import time
from slackclient import SlackClient
import requests
import jenkins_calls

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

user_validation_token = os.environ.get('USER_VALIDATION_TOKEN')
starterbot_id = None

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM


def get_username(user_id):
    """
    # get_username("UC8GQGE7P")
    :param user_id:
    :return: username
    """
    payload = {'token': user_validation_token, 'user': user_id}
    res = requests.get('https://slack.com/api/users.info', params=payload)
    return res.json()["user"]["name"], res.json()["user"]["real_name"]


def parse_message(slack_events):
    """
    :param slack_events:
    :return:
    """
    if len(slack_events):
        print slack_events
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id = event["user"]
                message = event["text"]
                (user_name, realname) = get_username(user_id)
                # import pdb
                # pdb.set_trace()
                if "help" == message.lower():
                    message = "Hello {}, Welcome to Jenkins BOT\n".format(realname)
                    message+= "Please follow below help to start interacting with Jenkins\n"
                    message+= "To get all available jobs in Jenkings type get-all-jobs\n"
                    message+="You can run a jenkins job by asking run:<jobname>\n"
                    message+="You can run a jenkins job with parameters by asking run:<jobname>,key1:value1,key2:value2\n"
                    message+="To get the status of job-status:<jobname>\n"
                    # message+="To clear all input parameters use #exit or #abort\n"
                    return message, event["channel"]
                elif "get-all-jobs" in message.lower():
                    conn = jenkins_calls.JenkinsSlack(username=user_name)
                    res = conn.get_all_jobs()
                    if res:
                        message = "The available jobs are:\n"
                        for each in res:
                            message+=each+"\n"
                        return message,event["channel"]

                elif "run:" in message.lower():
                    user_input_params = dict(item.split(":") for item in message.split(","))
                    job_name = user_input_params["run"]
                    #To Remove the name from Dict
                    user_input_params.pop("run", None)
                    conn = jenkins_calls.JenkinsSlack(username=user_name)
                    res = conn.get_job_info(job_name)
                    if res:
                        if res == True:
                            res = {}

                        key_list=[]
                        for each_param in res:
                            key_list.append(each_param['name'])
                        if len(key_list):
                            # if len(user_input_params.keys()):
                            ascii_user_input = set([x.encode('UTF8') for x in user_input_params.keys()])
                            # if set(key_list) < set(ascii_user_input):
                            if set(key_list).issubset(ascii_user_input):
                                if conn.build_job(job_name, parameters={}):
                                    message = "Build job for {} has been triggered\n".format(job_name)
                                    message += "To get the status of the job type in job-status:{}".format(job_name)
                                    return message, event["channel"]
                                else:
                                    return "Unknown error occured", event["channel"]
                            else:
                                message = "All parameters were not given to run the job\n"
                                args_list = ""
                                count = 0
                                for each_key in key_list:
                                    args_list += each_key + ":value{},".format(count)
                                    count += 1
                                args_list = args_list.rstrip(',')
                                message += "Please use syntax run:{},{}\n".format(job_name, args_list)
                                message += "Make sure to replace values with appropriate info"
                                return message, event["channel"]

                        else:
                            if conn.build_job(job_name, parameters={}):
                                message = "Build job for {} has been triggered\n".format(job_name)
                                message += "To get the status of the job type in job-status:{}".format(job_name)
                                return message, event["channel"]
                    else:
                        return "Invalid job name {}".format(job_name), event["channel"]
                elif "job-status:" in message.lower():
                    params = dict(item.split(":") for item in message.split(","))
                    job_name = params["job-status"]
                    conn = jenkins_calls.JenkinsSlack(username=user_name)
                    res = conn.get_job_status(job_name)
                    if res:
                        return "Status for {} job is {}".format(job_name,res), event["channel"]
                    else:
                        return "Invalid job name {}".format(job_name), event["channel"]
                else:
                    None,None
    else:
        print ".",
    return None, None

def handle_command(message, channel):
    """
        Executes bot command if the command is known
    """
    default_response = "Hello There, Welcome to Jenkins BOT\n"
    default_response += "Please follow below help to get communicate with Jenkins\n"
    default_response += "To get all available jobs in Jenkings type get-all-jobs\n"
    default_response += "You can run a jenkins job by asking run:<jobname>\n"
    default_response += "You can run a jenkins job with parameters by asking run:<jobname>,key1:value1,key2:value2\n"
    default_response += "To get the status of Job status:<jobname>\n"
    default_response += "To clear all input parameters use #exit or #abort\n"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        print starterbot_id

        while True:
            to_post_message, channel = parse_message(slack_client.rtm_read())
            if to_post_message:
                handle_command(to_post_message, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
