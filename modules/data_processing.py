import hashlib
import pandas as pd
#import data_creation - if you want to create a new datafile and use it, then use this. 
# df = data_creation.total_anns_df

#load the data from file
df = pd.read_json('hypothesis_v1__12-03-22.jsonl', orient='records', lines=True)

# A function to generate id from another column
def generate_id(string: str):
    return hashlib.sha1(string.encode("utf-8")).hexdigest()

# A function to generate new column for non-null valued 'text_' column 
def extract_text_from_target(row):
    if row["text"] != "":
        row["text_"] = row["text"]
    elif "selector" in row["target"][0]:
        row["text_"] = [s["exact"] for s in row["target"][0]["selector"] if s["type"] == "TextQuoteSelector"][0]
    else:
        row["text_"] = ""
    return row
df = df.apply(lambda row: extract_text_from_target(row), axis=1)

# Fill in the 'document' column value from the 'target' column field 'exact', convert dict -> str
def extract_text_from_document(row):
    if row["document"].get("title"):
        row["document"] = row["document"]["title"][0]
    elif "selector" in row["target"][0]:
        row["document"] = [s["exact"] for s in row["target"][0]["selector"] if s["type"] == "TextQuoteSelector"][0]
    else:
        row["document"] = ""
    return row
df = df.apply(lambda row: extract_text_from_document(row), axis = 1)

# Generate document id from 'document' values.
df['doc_id'] = df['document'].apply(lambda doc: generate_id(doc))

# Rename the column 'id' into 'ann_id'.

