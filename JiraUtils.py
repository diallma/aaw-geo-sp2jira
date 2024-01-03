from jira import JIRA
import os

jira_server = "https://jirab.statcan.ca"
jira_auth_token = os.environ.get("JIRA_TOKEN")
jira_project = "DASBOP"
jira_issue_type = "Epic"
jira_assignee = "luodan"
jira_watchers = ["zimmshe", "bonedan", "coutann"]

jira = JIRA(server=jira_server,
            token_auth=jira_auth_token)

def create_jira_issue_from_form_data(issue_summary, issue_desc):
    issue_dict = {
        'project': {'key': jira_project},
        'summary': issue_summary,
        # epic name field
        'customfield_10704': issue_summary,
        'description': issue_desc,
        'issuetype': {'name': jira_issue_type},
        'assignee': {'name': jira_assignee}
    }

    new_issue = jira.create_issue(fields=issue_dict)
    # this can't be done as part of issue creation, unfortunately
    for watcher in jira_watchers:
        jira.add_watcher(new_issue, watcher)

    return new_issue

def get_authenticated_user():
    return f"Authenticated user: {jira.myself()['name']}"
