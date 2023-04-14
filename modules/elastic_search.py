from typing import List

queries = [
    {
        "description": "search by id",
        "query": {
            "bool": {
                "must": {
                    "match_phrase": {
                        "_id": "4011af8ea429e3c113c7328a721f6a2af2fd188f_L5lt6s5MEeqm_pesYHJVVQ",
                    }
                },
            },
        }
    },
    {
        "description": "search documents by list of values in tags",
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "tags": "<LIST_OF_VALUES>"
                        }
                    }
                ]
            }
        }
    },
    {
        "description": "search document by document type",
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "tags": ["is:<TYPE>"]
                        }
                    }
                ]
            }
        }
    },
    {
        "description": "search documents in date range (where date is in 'text' field when the tags contain 'has:date' or 'has:date-approx'",
        "query": {
            "range": {
                "text": {
                    "gte": "<BEGIN_DATE>",
                    "lte": "<END_DATE>"
                }
            }
        }

    }
]

_queries = [
    {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "date": {
                                "gte": "2022-01-01",
                                "lte": "2022-12-31"
                            }
                        }
                    },
                    {
                        "terms": {
                            "tags": ["tag1", "tag2", "tag3"]
                        }
                    }
                ]
            }
        }
    }

]

query_text = {}
query_date_range = {}
query_type = {
    "terms": {
        "tags": "<LIST_TYPES>"
    }
}


def search_documents(text: str, date_range: List[str, str], type: str, ann_type, has_property: str,
                     keywords: List[str]) -> list:
    """
    Building a query for elastic search consisting of six subqueries, depending on what's provided

    :param text: free text to be search in the fields 'text' or 'document'
    :param date_range: a list with two values [begin_date, end_date]. When provided, we need to filter documents that have date and whose date is in the range
    :param type: relates to documents which have a tag "is:<TYPE>", where "<TYPE>" is the type provided
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
        pass

    if date_range:
        pass

    if type:
        pass
        query_type['terms']['tags'] = [type]
        query['query']['bool']['must'].append(query_type)


    res = es.search(index="hypothesis_v1", body={"query": query})
    for doc in res['hits']['hits']:
        print("%s) %s" % (doc['_source']['user'], doc['_source']['document']))

    return res['hits']['hits']

# search_documents(text="vaccination measures", date_range=["2020-05-01", "2020-06-01"], type="tweet", ann_type="doi", has_property="context", keywords=["COVID"])
