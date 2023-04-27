import data_processing
import data_structure
import queries
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


# [optional] If you don't have the data already, then run the following code as well. 
# import data_creation


# Initiate a client instance and call an API 
es = Elasticsearch("http://localhost:9200")
es.info().body

# load data from file
df3 = (
    pd.read_json('hypothesis_documents_v2.jsonl', orient='records', lines=True)
    .dropna()
    .sample(5000, random_state=42)
    .reset_index()
)
df3 = df3.drop(['index'], axis = 1) # Unnecessary column, index dropping.


#Create 'date' column to fill when there are 'has:date' or 'has:date-approx' in 'tags' -> use it later in date_range search
tags_to_check = ['has:date', 'has:date-approx'] # which directs the tags containing date information.

def get_ann_by_tag(row, tag_values):
    for tag in tag_values:
        if tag in row['tags']:
            row['date'] = row['text']
        else:
            row['date'] = ""
    return row
    
df3 = df3.apply(lambda row: get_ann_by_tag(row, tags_to_check), axis=1)

#Process mixed formatted values in 'date' column.
def date_format(date):
    if date != "":
        date = date.replace('\n', '')                # replace the Nonetype character to empty string.
        if len(date) == 4:                           # original format was YYYY 
            date = date + "-01-01" 
        if len(date) == 7 and date[0] == 0: 
            date = date[3:] + "-" + date[:2] + "-01" # original format was MM-YYYY
        if len(date) == 7 and date[0] != 0:          # original format was YYYY-MM
            date = date + "-01"
        if len(date) > 7:                            # original format had another character
            date = date.split(" ", 1)[0]
            if len(date) < 7: 
                date = date + "-01-01"
        return date
    else: 
        return date
df3['date'] = df3['date'].apply(lambda date: date_format(date))




# initiate a client instance and call an API. 
# queries.py does the job.


# create index to use in Elasticsearch 

mappings = {
    
    "properties": {
        "ann_id" : {"type": "keyword"}, 
        "parent_doc_id" : {"type": "keyword"}, 
        "document_uri" : {"type": "keyword"}, 
        "document" : {"type": "keyword"}, 
        "tags": {"type": "keyword"},
        "created" : {"type": "date"}, 
        "updated": {"type": "date"}, 
        "user": {"type": "keyword"}, 
        "text" : {"type": "text", "analyzer": "standard"}, 
        "date" : {"type": "date",
                "ignore_malformed": True},
        "group": {"type": "keyword"}, 
        "permissions": {"type": "nested"}, 
        "target": {"type": "nested"}, 
        "links": {"type": "nested"}, 
        "user_info": {"type": "object"}, 
        "flagged": {"type": "text", "analyzer": "standard"}, 
        "hidden": {"type": "text", "analyzer": "standard"}
        
    
    }
}

# untoggle and run if you've already created index with the same name before
es.options(ignore_status=[400,404]).indices.delete(index='hypothesis_v1') # delete if you've already created index with the same name before
es.indices.create(index= "hypothesis_v1", mappings = mappings)

#  add data to the index created above


bulk_data = []
for i,row in df3.iterrows():
    bulk_data.append(
        {
            "_index": "hypothesis_v1",
            "_id": row['ann_id'],
            "_source": {
                "parent_doc_id": row["parent_doc_id"],
                "document_uri": row["document_uri"],
                "document": row["document"], 
                "tags": row["tags"], 
                "created": row["created"], 
                "updated": row["updated"], 
                "user": row["user"], 
                "text": row["text"], 
                "date": row["date"],
                "group": row["group"], 
                "permissions": row["permissions"], 
                "target": row["target"], 
                "links": row["links"], 
                "user_info": row["user_info"], 
                "flagged": row["flagged"], 
                "hidden": row["hidden"]
                
                
            }
        }
    )

es.indices.refresh(index="hypothesis_v1")


# Search query
search_documents = queries.search_documents
 
 
print("\n----------------------------------------------")

# Search 'term' in 'text' field
search_documents(text = 'Search')
# Search document with a given 'tag'. 
search_documents(keywords = ['COVID-19', 'vaccination'])
# Search document with a date range. 
search_documents(date_range = ['2020', '2021'])
# Search document by type
search_documents(type_ = "twitter")
# Search document if they contains all the tags input
search_documents(keywords = ['COVID-19', 'pandemic', 'is:news','testing', 'tracking'])




