import pandas as pd
import SharepointUtils
import JiraUtils


# the column where the form stores the ID value. It seems to get populated only when data is submitted via the form.
ID_ROW = 0
FNAME_ROW = "First name"
LNAME_ROW = "Last name"
jira_issue_summary = "DAS Intake Form submission by {0} {1}"
jira_desc_no_response = "No Response"

# get the form data from sharepoint
df = SharepointUtils.get_intake_form_data_as_dataframe()

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
        new_issue = JiraUtils.create_jira_issue_from_form_data(issue_summary, issue_desc)
    except:
        print(f"Error creating JIRA issue from ID {current_id}")
    else:
        SharepointUtils.add_processed_id_to_list(current_id)
        issue_count += 1
        print(new_issue)

print(f"Process completed. {issue_count} issues created.")
