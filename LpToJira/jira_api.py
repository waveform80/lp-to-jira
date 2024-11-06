# The purpose of lp-to-jira is to take a launchad bug ID and create a new Entry
# in JIRA in a given project


import os
import json
from urllib.parse import urlparse

from jira import JIRA


class JiraAPI():
    def __init__(self, credstore=None):
        if credstore is not None:
            self.credstore = credstore
        else:
            snap_home = os.getenv("SNAP_USER_COMMON")
            if snap_home:
                self.credstore = "{}/.jira.token".format(snap_home)
            else:
                self.credstore = os.path.expanduser("~/.jira.token")

        try:
            with open(self.credstore) as f:
                config = json.load(f)
                self.server = str(config['jira-server'])
                self.login = str(config['jira-login'])
                self.token = str(config['jira-token'])
        except (FileNotFoundError, KeyError, ValueError):
            self.prompt_for_credentials()

    def prompt_for_credentials(self):
        print('JIRA Token information file {} could not be found or parsed.'.format(self.credstore))
        print('')
        s = input('Do you want to enter your JIRA token information now? (Y/n) ')
        if s.strip().lower() == 'n':
            raise ValueError("JIRA API isn't initialized")
        s = input('JIRA server address: ')
        url = urlparse(s)
        if not url.scheme:
            url = url._replace(schema='https')
        self.server = url.geturl()
        s = input('JIRA email login: ')
        # TODO Some rudimentary validation
        self.login = s
        api_url = 'https://id.atlassian.com/manage-profile/security/api-tokens'
        s = input('JIRA API Token (see {api_url}): '.format(api_url=api_url))
        # TODO Some rudimentary validation
        self.token = s
        s = input('Save these credentials for future use? (Y/n) ')
        if s.strip().lower() != 'n':
            try:
                data = {
                    'jira-server': self.server,
                    'jira-login': self.login,
                    'jira-token': self.token,
                }
                with open(self.credstore, 'w') as f:
                    json.dump(data, f)
            except (FileNotFoundError, json.JSONDecodeError):
                raise ValueError("JIRA API isn't initialized")
