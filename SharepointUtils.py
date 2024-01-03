from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io
import pandas as pd
import os

# sharepoint connection
client_id = os.environ.get("SHAREPOINT_CLIENT_ID") 
client_secret = os.environ.get("SHAREPOINT_CLIENT_SECRET")
client_creds = ClientCredential(client_id, client_secret)
site_url = "https://054gc.sharepoint.com/sites/DAaaSD-AllStaff-DADS-Touslesemployes"
ctx = ClientContext(site_url).with_credentials(client_creds)

#form data
# xslx can be found at https://054gc.sharepoint.com/:x:/r/sites/DAaaSD-AllStaff-DADS-Touslesemployes/_layouts/15/Doc.aspx?sourcedoc=%7B1C1CBFA7-E2E3-4BCF-8030-94C3A4384715%7D&file=Data%20Analytics%20Services%20(DAS)%20-%20Get%20started.xlsx&action=default&mobileredirect=true&cid=2ac2f7e2-eea5-471f-abe7-3614f5cb5fcd 
file_url = "/sites/DAaaSD-AllStaff-DADS-Touslesemployes/Shared%20Documents/CSU%20-%20UCS/DAaaS%20Intake%20Form/Data%20Analytics%20Services%20(DAS)%20-%20Get%20started%201.xlsx"
sheet_name = "Form1"

#processed id list data
# list can be found at https://054gc.sharepoint.com/sites/DAaaSD-AllStaff-DADS-Touslesemployes/Lists/Intake_form_last_id/AllItems.aspx
list_title = "Intake_form_processed_ids" #name of the list in sharepoint
list_column = "Title" #the list column containing ID data
list_max_return = 5000 #if we ever get more applications than this we'll have to adjust it


def get_intake_form_data_as_dataframe():
    # connect to sharepoint and get the xslx file
    response = File.open_binary(ctx, file_url)

    # save data to BytesIO stream
    bytes_file_obj = io.BytesIO()
    bytes_file_obj.write(response.content)
    bytes_file_obj.seek(0) #set file object to start

    # read excel file and each sheet into pandas dataframe 
    df = pd.read_excel(bytes_file_obj, sheet_name)
    # drop empty rows. inplace=True modifies the existing dataframe instead of returning a new one.
    df.dropna(inplace=True, subset=['ID'])
    # remove the already processed ids from the dataframe
    processed_ids = get_processed_id_list()
    df = df[df.ID.isin(processed_ids) == False]

    return df

def get_processed_id_list():
    # connect to sharepoint and get the list of IDs
    raw_list = ctx.web.lists.get_by_title(list_title)
    id_list = raw_list.items.get().select([list_column]).top(list_max_return).execute_query()

    print("Total number of processed applications before this run: {0}".format(len(id_list)))
    processed_id_list = []

    for index, item in enumerate(id_list):  # type: int, ListItem
        application_id = float(item.properties[list_column]) #convert to float to match dataframe
        processed_id_list.append(application_id)
    
    return processed_id_list

def add_processed_id_to_list(new_id):
    
    raw_list = ctx.web.lists.get_by_title(list_title)
    new_list_item_properties = {
        list_column: str(new_id) #need to convert back to string because sharepoint wants it that way
    }
    new_item = raw_list.add_item(new_list_item_properties).execute_query()
    return new_item
