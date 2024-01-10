
# Definining subqueries
query_text = {
    "match": {
        "text": {
            "query": "input_text", 
            "operator": "and"
        } 
    }
}

query_date_range = {
    
    "range": {
        "date": {    
            "gte": "begin_date",
            "lte": "end_date"
        }
    }
    
}


query_type = {
    "term" : { "tags" : "TYPE" }
}

query_ann_type = {   
    "term" : { "tags" : "ANN_TYPE" }
}

query_has_property = {
    "term" : { "tags" : "HAS_PROPERTY" }
}

#temp_keywords = ["str1", "str2", "str3"]
# query_keywords = [{"term": {"tags": keyword}} for keyword in temp_keywords] -> it is already inside the function search_documents
