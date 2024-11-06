# The purpose of lp-to-jira is to take a launchad bug ID and create a new Entry
# in JIRA in a given project


import os
import json

from jira import JIRA

class jira_api():
    def __init__(self,credstore="{}/.jira.token".format(os.path.expanduser('~'))):
        snap_home = os.getenv("SNAP_USER_COMMON")
        if snap_home:
            self.credstore = "{}/.jira.token".format(snap_home)
        else:
            self.credstore = credstore
        try:
            with open(self.credstore) as f:
                config = json.load(f)
                self.server = config['jira-server']
                self.login = config['jira-login']
                self.token = config['jira-token']
        except (FileNotFoundError, json.JSONDecodeError):
            print('JIRA Token information file {} could not be found or parsed.'.format(self.credstore))
            print('')
            gather_token = input('Do you want to enter your JIRA token information now? (Y/n) ')
            if gather_token == 'n':
                raise ValueError("JIRA API isn't initialized")
            self.server = input('Please enter your jira server address : ')
            self.login = input('Please enter your email login for JIRA : ')
            self.token = input('Please enter your JIRA API Token (see https://id.atlassian.com/manage-profile/security/api-tokens) : ')
            save_token = input('Do you want to save those credentials for future use or lp-to-jira? (Y/n) ')
            if save_token != 'n':
                try:
                    data = {
                        'jira-server': self.server,
                        'jira-login': self.login,
                        'jira-token': self.token,
                    }
                    with open(self.credstore,'w+') as f:
                        json.dump(data, f)
                except (FileNotFoundError, json.JSONDecodeError):
                    raise ValueError("JIRA API isn't initialized")
