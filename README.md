# Knowledge Base

## Pipeline

### 0. [Optional] Fetch data from Hypothes.is and dump it into jsonl.
### 1. Load data from hypothes.is file
### 2. Data Description
Following observations were made
1. Brief description of columns
2. How many properties ("has:")
3. How many 
4. How many document types (found in tags is:...)
4. 

### 3. Data Curation
The following changes were applied to consolidate and curate the data
1. There is a column called "text", but it's not always filled. The text lies sometimes within the value of the "target" column. The following rule is followed:  

``` {pseudocode}
if text != "", take it as text;
elif text is in target (found within 'selector' as 'TextQuoteSelector') -> take that text;
else text = ""
```

2. There is no id to idenfify specific annotations
3. 

### 4. Data Structuring - Reference document

### 5. Generation of documents to ingest

### 6. 

----

### TODO

- [ ] Complete Readme as documentation so that someone can understand the overall process without reading the Jupyter Notebook.
- [ ] From Jupyter Notebook to python module: pipeline.py + all needed functions in modules.
- [ ] Think & write "top 5 obvious" queries for elastic search. Examples:
  - Q1: search "term" in "text" field.
  - Q2: search all documents with tag "X"
  - Q3: 