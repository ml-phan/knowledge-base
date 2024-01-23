import pandas as pd


def search_documents(es, text: str = None, date_range: list[str] = None,
                     type_: str = None, ann_type=None,
                     has_property: str = None,
                     keywords: list[str] = None,
                     query_size=20) -> list:
    """
    Building a query for elastic search consisting of six sub queries,
    depending on what's provided

    :param query_size: the number of results to be returned
    :param es: the ElasticSearch instance to be used for searching
    :param text: free text to be search in the fields 'text' or 'document'
    :param date_range: a list with two values [begin_date, end_date].
    When provided, we need to filter documents that have date and whose date
    is in the range
    :param type_: relates to documents which have a tag "is:<TYPE>",
    where "<TYPE>" is the type provided
    :param ann_type: relates to documents which have a tag "ann:<ANN_TYPE>",
    where "<ANN_TYPE>" is the ann_type provided
    :param has_property: relates to documents which have a tag
    "has:<HAS_PROPERTY>", where "<HAS_PROPERTY>" is the has_property provided
    :param keywords: list of terms expected to be found in the "tags" field
    ONLY, and they appear without any specification (not "is:", "has:, "ann:")
    :return: a list of results with all relevant documents for that query
    """

    query = {
        "from": 0,
        "size": query_size,
        "query": {
            "bool": {
                "filter": [],
                "must": []
            }
        }
    }

    # Defining sub queries
    query_text = {
        "match": {
            "text": {
                "query": "input_text",
                "operator": "and"
            }
        }
    }
    # Is it 'match' or 'match_phrase' or something else?
    query_date_range = {

        "range": {
            "date": {
                "gte": "begin_date",
                "lte": "end_date"
            }
        }

    }
    # Is it 'text' or something else?
    query_type = {
        "term": {"tags": "TYPE"}
    }
    query_ann_type = {
        "term": {"tags": "ANN_TYPE"}
    }
    query_has_property = {
        "term": {"tags": "HAS_PROPERTY"}
    }
    temp_keywords = ["str1", "str2", "str3"]
    if text:
        query_text['match']['text']['query'] = text
        query['query']['bool']['filter'].append(query_text)

    if date_range:

        if len(date_range) > 1:
            query_date_range['range']['date']['gte'] = date_range[0]
            query_date_range['range']['date']['lte'] = date_range[1]
            query['query']['bool']['filter'].append(query_date_range)

        elif len(date_range) == 1:
            query_date_range['range']['date']['gte'] = date_range[
                0]  # only one date -> putting it to a starting date.
            query_date_range['range']['date']['lte'] = '3000-01-01'
            query['query']['bool']['filter'].append(query_date_range)

            print(query)

        else:
            pass

    if type_:
        query_type['term']['tags'] = "is:" + type_
        query['query']['bool']['filter'].append(query_type)

    if ann_type:
        query_ann_type['term']['tags'] = "ann:" + ann_type
        query['query']['bool']['filter'].append(query_ann_type)

    if has_property:
        query_has_property['term']['tags'] = "has:" + has_property
        query['query']['bool']['filter'].append(query_has_property)

    if keywords:
        temp_keywords = keywords
        query_keywords = [{"term": {"tags": keyword}} for keyword in
                          temp_keywords]
        query['query']['bool']['must'].extend(query_keywords)

    index_name = get_es_index_name(es)
    res = es.search(index=index_name, query=query['query'], size=query_size)

    for doc in res['hits']['hits']:
        print("%s) %s" % (doc['_source']['user'], doc['_source']['document']))

    return res


def search_id(es, ann_id):
    index_name = get_es_index_name(es)
    resp = es.search(
        index=index_name,
        body={
            "from": 0,
            "size": 20,
            "query": {
                "bool": {
                    "filter": {
                        "match_phrase": {
                            "_id": ann_id,
                        }
                    },
                },
            },
        }
    )
    return resp


def search_tag(es, tags: list):
    index_name = get_es_index_name(es)
    return es.search(index=index_name, query={"terms": {"tags": tags}})


def get_es_index_name(es):
    return [index["index"] for index in es.cat.indices(format="json")][0]


def result_format(response):
    doc_list = []
    text_list = []
    uri_list = []
    tags_list = []
    date_list = []
    for item in response["hits"]["hits"]:
        doc_list.append(item["_source"]["document"])
        text_list.append(item["_source"]["text"])
        uri_list.append(item["_source"]["document_uri"])
        tags_list.append(item["_source"]["tags"])
        date_list.append(item["_source"]["date"])
    resp_df = pd.DataFrame({"Document": doc_list,
                            "Text": text_list,
                            "Tags": tags_list,
                            "URI": uri_list,
                            "Date": date_list
                            },
                           index=range(1, len(doc_list) + 1)
                           )
    return resp_df
