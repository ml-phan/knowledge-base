#import data_processing
#import data_structure
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import queries
import pandas as pd
from typing import List



# [optional] If you don't have the data already, then run the following code as well. 
# import data_creation
# df = data_creation.total_anns_df

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
    
bulk(es, bulk_data)

es.indices.refresh(index="hypothesis_v1")

# Subqueries from 'queries' to use in query generation function.
query_text = queries.query_text
query_date_range = queries.query_date_range
query_type = queries.query_type
query_ann_type = queries.query_ann_type
query_has_property = queries.query_has_property


# Search query function
def search_documents(text: str = None , date_range: List[str] = None , type_: str = None, ann_type = None, has_property: str = None,
                     keywords: List[str] = None) -> list:
    """
    Building a query for elastic search consisting of six subqueries, depending on what's provided

    :param text: free text to be search in the fields 'text' or 'document'
    :param date_range: a list with two values [begin_date, end_date]. When provided, we need to filter documents that have date and whose date is in the range
    :param type_: relates to documents which have a tag "is:<TYPE>", where "<TYPE>" is the type provided
    :param ann_type: relates to documents which have a tag "ann:<ANN_TYPE>", where "<ANN_TYPE>" is the ann_type provided
    :param has_property: relates to documents which have a tag "has:<HAS_PROPERTY>", where "<HAS_PROPERTY>" is the has_property provided
    :param keywords: list of terms expected to be found in the "tags" field ONLY and they appear without any specification (not "is:", "has:, "ann:")
    :return: a list of results with all relevant documents for that query
    """
    
    query = {
        "query": {
            "bool": {
                "filter": [], 
                "must": []
            }
        }
    }

    if text:
        query_text['match']['text']['query'] = text
        query['query']['bool']['filter'].append(query_text)

        
    if date_range:
        
        if len(date_range) > 1:
            query_date_range['range']['date']['gte'] = date_range[0]
            query_date_range['range']['date']['lte'] = date_range[1]
            query['query']['bool']['filter'].append(query_date_range)
            
        elif len(date_range) == 1: 
            query_date_range['range']['date']['gte'] = date_range[0] # only one date -> putting it to a starting date.
            query_date_range['range']['date']['lte'] = '3000-01-01'
            query['query']['bool']['filter'].append(query_date_range)
            
            print(query)
            
        else: 
            pass
    
        
    if type_:
        query_type['term']['tags'] = "is:"+ type_
        query['query']['bool']['filter'].append(query_type)
        
    if ann_type: 
        query_ann_type['term']['tags'] = "ann:"+ann_type
        query['query']['bool']['filter'].append(query_ann_type)
    
    if has_property: 
        query_has_property['term']['tags'] = "has:"+has_property
        query['query']['bool']['filter'].append(query_has_property)
        
    if keywords: 
        temp_keywords = keywords
        query_keywords = [{"term": {"tags": keyword}} for keyword in temp_keywords]
        query['query']['bool']['must'].extend(query_keywords)
    
    res = es.search(index="hypothesis_v1", query = query['query'])  
    
    for doc in res['hits']['hits']:
         print("%s) %s" % (doc['_source']['user'], doc['_source']['document']))
    
    return res['hits']['hits']

 
print("\n----------------------------------------------")

# Search 'term' in 'text' field
print(search_documents(text = 'Search'))
# Search document with a given 'tag'. 
print(search_documents(keywords = ['COVID-19', 'vaccination']))
# Search document with a date range. 
print(search_documents(date_range = ['2020', '2021']))
# Search document by type
print(search_documents(type_ = "twitter"))
# Search document if they contains all the tags input
print(search_documents(keywords = ['COVID-19', 'pandemic', 'is:news','testing', 'tracking']))




