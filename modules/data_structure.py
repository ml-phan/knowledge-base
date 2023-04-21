import pandas as pd 
import data_processing

df = data_processing.df
print(df)

# #load the data from file
# df = pd.read_json('hypothesis_v1__12-03-22.jsonl', orient='records', lines=True)

# Give the id column the name ann_id.
df = df.rename(columns={'id': 'ann_id'})

# DOCUMENT - Reference usage
# define a function to generate the document format 
def generate_document(df: pd.DataFrame) -> dict:
    
    """
    :param df: This dataframe is actually a "grouped-by" dataframe, meaning that doc_id, uri, document and tags are the same for all rows
    :return:
    """
    assert len(df['doc_id'].unique()) == 1
    assert len(df['document'].unique()) == 1

    document = {
        "_id": df['doc_id'].iloc[0],
        "document_uri": df["uri"].iloc[0],
        "document": df['document'].iloc[0],
        "tags": [],
        "annotations": [], 
        "created": df['created'].iloc[0], 
        "updated": df['updated'].iloc[0], 
        "user": df['user'].iloc[0], 
        "group": df['group'].iloc[0], 
        "permissions": df['permissions'].iloc[0], 
        "user_info": df['user_info'].iloc[0], 
        "flagged": df['flagged'].iloc[0], 
        "hidden": df['hidden'].iloc[0]
        
    }

    for i, row in df.iterrows():
        annotation = {}
        # this is at level of document (first level)
        document["tags"] += row["tags"]

        # This is at level of annotation (second level)
        annotation["text"] =  row["text_"]
        annotation["tags"] = row["tags"]
        annotation["ann_id"] = row["ann_id"]
        annotation["target"] = row["target"]
        annotation["links"] = row["links"]
        document["annotations"].append(annotation)

    return document

# Generate documents format from dataframe. 
documents = []

for doc_id in df['doc_id'].unique():
    sub_df = df.query("doc_id == @doc_id")
    documents.append(generate_document(sub_df))



# ATTENTION! This block of codes will overwrite existing file if it already does.
# Save the document to jsonl
import json
with open('hypothesis_documents_v1.jsonl', 'w') as f:
    for doc in documents:
        try:
            f.write(json.dumps(doc, ensure_ascii=False, default = str) + '\n')
        except:
            print(doc)
            raise Exception
        

# DOCUMENT - Object to ingest into ElasticSearch
# function to generate document format
def generate_document3(df: pd.DataFrame) -> dict:
    """
    
    :param df: This dataframe is actually a "grouped-by" dataframe, meaning that doc_id, uri, document and tags are the same for all rows
    :return:
    
    """
    assert len(df['doc_id'].unique()) == 1
    assert len(df['document'].unique()) == 1

    document = {
        "ann_id": df['doc_id'].iloc[0] + "_" + df['ann_id'].iloc[0],
        "parent_doc_id": df['doc_id'].iloc[0],
        "document_uri": df["uri"].iloc[0],
        "document": df['document'].iloc[0],
        "tags": df['tags'].iloc[0], 
        "created": df['created'].iloc[0], 
        "updated": df['updated'].iloc[0], 
        "user": df["user"].iloc[0],
        "text": df["text"].iloc[0],
        "group": df["group"].iloc[0], 
        "permissions": df["permissions"].iloc[0], 
        "target": df["target"].iloc[0], 
        "links": df["links"].iloc[0], 
        "user_info": df["user_info"].iloc[0], 
        "flagged": df["flagged"].iloc[0], 
        "hidden": df["hidden"].iloc[0], 
        
    }

    
    return document

# Object to ingest
documents_es = []

for doc_id in df['doc_id'].unique():
    sub_df = df.query("doc_id == @doc_id")
    documents_es.append(generate_document3(sub_df))



# ATTENTION! This block of codes will overwrite existing file if it already does.
# Save the document to jsonl
import json
with open('hypothesis_documents_v2.jsonl', 'w') as f:
    for doc in documents_es:
        try:
            f.write(json.dumps(doc, ensure_ascii=False, default = str) + '\n')
        except:
            print(doc)
            raise Exception

