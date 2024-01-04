import os
import pandas as pd
from JiraUtils import JiraUtils
from SharepointUtils import SharepointUtils

# initialize JIRA
jira_server = "https://jirab.statcan.ca"
jira_auth_token = os.environ.get("JIRA_TOKEN")
jira_project = "DASBOP"
jira_issue_type = "Epic"
jira_assignee = "luodan"
# https://stackoverflow.com/questions/31352317/how-to-pass-a-list-as-an-environment-variable
jira_watchers = ["zimmshe", "bonedan", "coutann"]

jira = JiraUtils(jira_server, jira_auth_token, jira_project, jira_issue_type, jira_assignee, jira_watchers)

# sharepoint connection
client_id = os.environ.get("SHAREPOINT_CLIENT_ID") 
client_secret = os.environ.get("SHAREPOINT_CLIENT_SECRET")
site_url = "https://054gc.sharepoint.com/sites/DAaaSD-AllStaff-DADS-Touslesemployes"

#form data
# xslx can be found at https://054gc.sharepoint.com/:x:/r/sites/DAaaSD-AllStaff-DADS-Touslesemployes/_layouts/15/Doc.aspx?sourcedoc=%7B1C1CBFA7-E2E3-4BCF-8030-94C3A4384715%7D&file=Data%20Analytics%20Services%20(DAS)%20-%20Get%20started.xlsx&action=default&mobileredirect=true&cid=2ac2f7e2-eea5-471f-abe7-3614f5cb5fcd 
file_url = "/sites/DAaaSD-AllStaff-DADS-Touslesemployes/Shared%20Documents/CSU%20-%20UCS/DAaaS%20Intake%20Form/Data%20Analytics%20Services%20(DAS)%20-%20Get%20started%201.xlsx"
sheet_name = "Form1"

#processed id list data
# list can be found at https://054gc.sharepoint.com/sites/DAaaSD-AllStaff-DADS-Touslesemployes/Lists/Intake_form_last_id/AllItems.aspx
list_title = "Intake_form_processed_ids" #name of the list in sharepoint
list_column = "Title" #the list column containing ID data
list_max_return = 5000 #if we ever get more applications than this we'll have to adjust it

sputils = SharepointUtils(client_id, client_secret, site_url, file_url, sheet_name, list_title, list_column, list_max_return)


# the column where the form stores the ID value. It seems to get populated only when data is submitted via the form.
ID_ROW = 0
FNAME_ROW = "First name"
LNAME_ROW = "Last name"
jira_issue_summary = "DAS Intake Form submission by {0} {1}"
jira_desc_no_response = "No Response"

# get the form data from sharepoint
df = sputils.get_intake_form_data_as_dataframe()

## go through each row and create a JIRA issue, saving processed IDs to the sharepoint list so we don't create them again later
issue_count = 0
for index, row in df.iterrows():

    current_id = row[ID_ROW]
    issue_desc = ""
    issue_summary = jira_issue_summary.format(row[FNAME_ROW], row[LNAME_ROW])
    
    for rowindex, rowval in row.items():
        issue_desc += f"{rowindex} : \n"
        if pd.isna(rowval):
            issue_desc += f"*{jira_desc_no_response}*\n\n"
        else:
            issue_desc += f"*{rowval}*\n\n"

    print(f"JIRA issue to be created from row id: {current_id}")
    print(f"Summary: {issue_summary}")
    #print(issue_desc) #left for debug

    try:
        new_issue = jira.create_jira_issue_from_form_data(jira_project, jira_issue_type, jira_assignee, issue_summary, issue_desc, jira_watchers)
    except:
        print(f"Error creating JIRA issue from ID {current_id}")
    else:
        sputils.add_processed_id_to_list(current_id)
        issue_count += 1
        print(new_issue)

print(f"Process completed. {issue_count} issues created.")
