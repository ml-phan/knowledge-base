from typing import List
import pandas as pd
import data_processing
from elasticsearch import Elasticsearch



# Initiate a client instance and call an API 
es = Elasticsearch("http://localhost:9200")
es.info().body

# Definining subqueries
query_text = {
    "match": {
        "text": "string"
    }
}
# Is it 'match' or 'match_phrase' or something else?

query_date_range = {
    
    "range": {
        
        "text": {    
            "gte": "begin_date", 
            "lte": "end_date"
        }
    }
    
}
# Is it 'text' or something else? 

query_type = {
    "terms": {
        "tags": "<LIST_TYPE>"
    }
}

query_ann_type = {   
    "terms" : {
        "tags": "<LIST_ANN_TYPES>"
    }
}

query_has_property = {
    "terms": {
        "tags": "<LIST_PROPERTY>"
    }
}


query_keywords = {
    "terms": {
        "tags": "TERM_TAGS"
    }
}

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
                "must": []
            }
        }
    }

    if text:
        query_text['match']['text'] = text
        query['query']['bool']['must'].append(query_text)

    if date_range:
        query_date_range['range']['text']['gte'] = date_range[0]
        query_date_range['range']['text']['lte'] = date_range[1]
        query['query']['bool']['must'].append(query_date_range) #'query' - 'range' should be? or is it okay?    

        
    if type_:
        query_type['terms']['tags'] = ["is:"+ type_]
        query['query']['bool']['must'].append(query_type)
        
    if ann_type: 
        query_ann_type['terms']['tags'] = ["ann:"+ann_type]
        query['query']['bool']['must'].append(query_ann_type)
    
    if has_property: 
        query_has_property['terms']['tags'] = ["has:"+has_property]
        query['query']['bool']['must'].append(query_has_property)
    
    if keywords: 
        query_keywords['terms']['tags'] = keywords
        query['query']['bool']['must'].append(query_keywords)
    

    res = es.search(index="hypothesis_v1", body={"query": query['query']})
    for doc in res['hits']['hits']:
        print("%s) %s" % (doc['_source']['user'], doc['_source']['document']))

    return res['hits']['hits']

