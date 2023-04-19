import data_processing
import data_structure
from modules.queries import search_documents
import queries
import pandas as pd
from elastic_search import Elasticsearch
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

# initiate a client instance and call an API. 
# queries.py does the job.

# create index to use in Elasticsearch 

mappings = {
    
    "properties": {
        "ann_id" : {"type": "text", "analyzer": "standard"}, 
        "parent_doc_id" : {"type": "text", "analyzer": "standard"}, 
        "document_uri" : {"type": "text", "analyzer": "standard"}, 
        "document" : {"type": "text", "analyzer": "standard"}, 
        "tags": {"type": "keyword"},
        "created" : {"type": "date"}, 
        "updated": {"type": "date"}, 
        "user": {"type": "text", "analyzer": "standard"}, 
        "text" : {"type": "text", "analyzer": "standard"}, 
        "group": {"type": "text", "analyzer": "standard"}, 
        "permissions": {"type": "nested"}, 
        "target": {"type": "nested"}, 
        "links": {"type": "nested"}, 
        "user_info": {"type": "object"}, 
        "flagged": {"type": "text", "analyzer": "standard"}, 
        "hidden": {"type": "text", "analyzer": "standard"}
        
    
    }
}

es.indices.create(index= "hypothesis_v1", mappings = mappings) # actual creation of the index here.

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
search_documents(type_= "twitter", keywords = "COVID-19")
search_documents(text="BBC News", has_property="context")
search_documents(date_range = ["2011-01-06", "2023-04-19"])
search_documents(type_ = "news")
search_documents(text = "BBC News", date_range = ['2021-01-01', '2023-04-01'], type_ = "news", has_property = "context", keywords = "COVID-19")





