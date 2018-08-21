
from jenkinsapi.jenkins import Jenkins
import os
import sys
import ConfigParser


class JenkinsSlack(object):
    def __init__(self,username):
        CurrDir = os.path.dirname(os.path.realpath(__file__))
        PropertiesDir = CurrDir + "/Properties/"
        ConfigFile = PropertiesDir + "Config.cfg"
        # self.username = username
        if os.path.isfile(ConfigFile) == False:
            print "Properties File " + "Config.cfg" + " Doesn't exits at " + PropertiesDir
            sys.exit(10)
        config = ConfigParser.ConfigParser()
        try:
            config.readfp(open(ConfigFile))
            # self.config = config
            JENKINS_URL = config.get('Jenkins', 'JENKINS_URL')
            try:
                token = config.get('usermappings', username)
            except Exception as Err:
                raise Exception("Invalid User",username)
            try:
                jen_con_obj = Jenkins(JENKINS_URL, username=username, password=token)
                self.jen_con_obj = jen_con_obj
            except Exception as error:
                print error
                sys.exit(100)
        except IOError as e:
            print (e)
            print "Error : Properties file not found"
            sys.exit(10)


    def jenkins_connection(self):
        # config = self.ReadConfig()
        JENKINS_URL = self.config.get('Jenkins', 'JENKINS_URL')
        token = self.config.get('usermappings',self.username)

        try:
            jen_con_obj = Jenkins(JENKINS_URL, username=self.username, password=token)
            self.jen_con_obj = jen_con_obj
        except Exception as error:
            print error
            sys.exit(100)

    def get_all_jobs(self):
        """
        :return: Returns list of all Availale Jobs
        """
        return self.jen_con_obj.keys()


    def get_job_info(self, JOB_NAME):
        """
        :param JOB_NAME:
        :return:
        """
        try:
            job = self.jen_con_obj.get_job(JOB_NAME)
        except Exception as err:
            print "Invalid Job {}".format(JOB_NAME)
            return False

        params = []
        if job.has_params():
            each_param = {}
            for each_key in job.get_params():
                each_param = {}
                each_param["name"] = each_key["name"]
                each_param["description"] = each_key["description"]
                each_param["type"] = each_key["type"]
                if each_key.get("choices"):
                    each_param["choices"] = each_key.get("choices")
                params.append(each_param)
            return params
        else:
            return True

    def build_job(self,JOBNAME,parameters={}):
        """
        :param JOBNAME:
        :return:
        """

        try:
            out = self.jen_con_obj.build_job(JOBNAME, params=parameters)
            print out, "Triggered the Job", JOBNAME
            return True
        except Exception as err:
            print err
            return False

    def get_job_status(self, JOB_NAME):
        """
        :param JOB_NAME:
        :return:
        """
        try:
            job = self.jen_con_obj.get_job(JOB_NAME)
        except Exception as err:
            print "Invalid Job {}".format(JOB_NAME), err
            return False

        running = job.is_queued_or_running()
        if not running:
           latestBuild = job.get_last_build()
           return latestBuild.get_status()


