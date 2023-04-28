# Knowledge Base

## Pipeline

### 0. [Optional] Fetch data from Hypothes.is and dump it into jsonl.
### 1. Load data from jsonl file.
### 2. Data Description
Following observations were made
1. Brief description of columns
2. How many properties exist can be found in tags "has:..."
3. How many document types exist is found in tags "is:..." 
4. The total number of tags and each quantity of unique tags
5. Field 'source' inside the 'target' column has identical values with 'uri' column. 

### 3. Data Curation
The following changes were applied to consolidate and curate the data
1. There is a column called "text", but it's not always filled. The text lies sometimes within the value of the "target" column. The following rule is followed:  

``` {pseudocode}
if text != "", take it as text;
elif text is in target (found within 'selector' as 'TextQuoteSelector') -> take that text;
else text = ""
```

2. There is no id to idenfify specific annotations. After checking if column 'id' can be identifier, let the 'id' become the annotation id.

```{pseudocode}
if number of rows in data == number of unique values in 'id'; 
  rename 'id' to 'ann_id'

```
3. Also, there is no identifier for document. We compare the number of unique values from 'uri' and 'document' column and found out that multiple uris direct to one document. Extract string value from 'document' and convert it to hexadecimal format which works as an id.

```{pseudocode}
func: extract_text_from_document
func: generate_id

data = data.apply(extract_text_from_document); 
'doc_id' = data.apply(generate_id('document'));

```
### 4. Data Structuring - Reference document

This document structure is built for reference usage, not to use directly in elasticsearch. 

**Steps**
1. Group dataset by doc_id
2. The top level of the document object comes from properties across rows (groupby) meaning that all the rows in that group have these same properties
3. The object annotations contains all the info coming from individual rows within the group
4. Save the document to jsonl.


```{pseudocode}
def generate_document(DataFrame) -> dict {

  _id = 'doc_id',
  document_uri = 'uri', 

  ... for all the columns not included in the below objects;
  
    for index, row in df.iterrows(){

          annotation = dict;
          document['tags'] += row['tags'];
          
          annotation['text'] =  row['text_'];
          annotation['tags'] = row['tags'];
          annotation['ann_id'] = row['ann_id'];
          annotation['target'] = row['target'];
          annotation['links'] = row['links'];

          document['annotations'] <- add(annotation)

    }

  return document;

}

```
### 5. Generation of documents to ingest

**Steps**
1. Group dataset by ann_id
2. The objects inside the dataset includes document information where the annotations are made by the name of variables
3. Save the documents to jsonl 


```{pseudocode}
def generate_document3(DataFrame) -> dict {

  document = {
        "ann_id": 'doc_id' + "_" + 'ann_id',
        "parent_doc_id": 'doc_id',
        "document_uri": 'uri',
        "document": 'document',
        "tags": 'tags', 
        "created": 'created', 
        "updated": 'updated', 
        "user": 'user',
        "text": 'text',
        "group": 'group', 
        "permissions": 'permissions', 
        "target": 'target', 
        "links": 'links', 
        "user_info": 'user_info', 
        "flagged": 'flagged', 
        "hidden": 'hidden', 
        
    }
    
    return document;

}

```



### 6. Search in ElasticSearch

0. Pre-step
    1. Run the docker in local environment
    2. Create the virtual environment - terminal command
    ```{pseudocode}
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    3. Run the Elasticsearch on docker - terminal command 
    ```{pseudocode}
    docker run --rm -p 9200:9200 -p 9300:9300 -e "xpack.security.enabled=false" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.3.3
    ```

1. Initiate a client instance and call an API.  
  ```{pseudocode}
  es = Elasticsearch("http://localhost:9200")
  es.info().body
  ```



2. Create an index for our document
    1. Assigning field data type. This let the computer know which kind of data the field contians. [For more](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html)
    2. Mapping
    ```{pseudocode}
    mappings = {
      
      "properties": {
          "ann_id" : {"type": "text", "analyzer": "standard"}, 
          "parent_doc_id" : {"type": "text", "analyzer": "standard"}, 
          ...
          -> assign all the objects in document for ingestion. 
      }
    }
    ```
3. Add data to the index created above. Then, load the data in bulk with the given index made above 'mapping' step.

  ```{pseudocode}
  bulk_data = []
  for i,row in df3.iterrows():
    bulk_data.append(
        {
            "_index": "hypothesis_v1",
            "_id": row['ann_id'],
            "_source": {
                "parent_doc_id": row["parent_doc_id"],
                "document_uri": row["document_uri"],
                ... for all the other objects.             
            }
        }
    )
  bulk(es, bulk_data)


  ```
4. Search the data with ElasticSearch
    1. Given annotation id, search the annotation. 
  
  ```{pseudocode}
  resp = es.search(
    index="hypothesis_v1",
    body={
        "query": {
            "bool": {
                "must": {
                    "match_phrase": {
                        "_id": "4011af8ea429e3c113c7328a721f6a2af2fd188f_L5lt6s5MEeqm_pesYHJVVQ",
                    }
                },
                },
        },            
    }
  )
  resp
  ```

### TODO list

- [x] Complete Readme as documentation so that someone can understand the overall process without reading the Jupyter Notebook.
- [ ] From Jupyter Notebook to python module: pipeline.py + all needed functions in modules.
- [x] Think & write "top 5 obvious" queries for elastic search. Examples:
  - Q1: search "term" in "text" field.
    - Q1.1: Compound search AND / OR for multiple text fields.
  - Q2: search all documents with tag "X" in the list tags.
  - Q3: get all documents in date range.
  - Q4: get documents by type - we need to offer a list of types ("is:...")

- [ ] Complete the search_documents function and provide 5 test cases combining different options.

---
- [ ] Options to parse natural language queries into our queries.
- [ ] Can we fetch the tweets??
- [ ] Can we fetch some info about the websites / videos??

#### Corrections

- Dates are sometimes not cleean enough - "2020-05\n"
- "is:twitter" and "is:tweet" should be merged
- "has:date" and "has date" should me merged

