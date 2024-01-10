import datetime
import hashlib
import json
import pickle
import time
from pathlib import Path

import pandas as pd
import requests
from elasticsearch import Elasticsearch

from modules.search import search_id

URL_SEARCH = r"https://api.hypothes.is/api/search"
GROUP = "Jk8bYJdN"
API_KEY = "my_api_key"


def fetch_all_data() -> pd.DataFrame:
    """
    Fetch all data from our group via Hypothe.is API.
    Concatenate all entries into a single Pandas Dataframe
    :return: pd.Dataframe
    """
    data_per_user = []

    start = time.perf_counter()
    users = requests.get(
        url=f"https://api.hypothes.is/api/groups/{GROUP}/members")
    for user in users.json():
        user_id = user['userid']
        print(f"\r Fetching data from {user_id}", end="")
        for i in range(0, 10000, 200):
            res = requests.get(url=URL_SEARCH,
                               params={'group': GROUP,
                                       'user': f'{user_id}', 'limit': 200,
                                       'offset': i},
                               headers={
                                   'Authorization': f"Bearer {API_KEY}"})
            if i > res.json()["total"]:
                break
            data_per_user.append(res.json())
    end = time.perf_counter()
    print(f"\nFetching time: {end - start:.2f} seconds")
    database = []
    for user in data_per_user:
        for item in user["rows"]:
            database.append(item)
    dataframe = pd.DataFrame(database)

    return dataframe


def check_database_update():
    """
    Check if the local database is up-to-date by comparing the entry number.
    Option to force update.
    :return: None
    """
    print("Checking database for updates...")
    users = requests.get(
        url=f"https://api.hypothes.is/api/groups/{GROUP}/members")
    user_ids = [user["userid"] for user in users.json()]
    user_annots = {}
    for user_id in user_ids:
        res = requests.get(url=URL_SEARCH,
                           params={'group': 'Jk8bYJdN', 'user': f'{user_id}',
                                   'limit': 1, 'offset': 0},
                           headers={
                               'Authorization': f"Bearer {API_KEY}"})
        if res.json()["total"] > 0:
            user_annots[user_id] = res.json()["total"]
    df = pd.read_pickle(list(Path(r"../data/").glob("*hypo*"))[-1])
    if sum(user_annots.values()) == len(df):
        print(
            f"The database size doesn't seem to have changed ({len(df)} entries).")
        while True:
            user_input = input(
                "Do you want to re-fetch the database anyway (y/n)? ")
            if user_input == 'y':
                data_pipeline()
                break
            elif user_input == 'n':
                break
            else:
                print("Invalid input. ", end="")


def create_tag_columns(row):
    """
    Create new columns with only terms and the annotation fields -
    is, has, ann, lang.
    :param row: pd.Dataframe row
    :return: pd.Dataframe row
    """
    row['is:'] = []
    row['has:'] = []
    row['ann:'] = []
    row['lang:'] = []
    row['terms_tags'] = []
    for tag in row['tags']:
        if 'is:' in tag:
            row['is:'].append(tag.split(':')[1])
        elif 'has:' in tag:
            row['has:'].append(tag.split(':')[1])
        elif 'ann:' in tag:
            row['ann:'].append(tag.split(':')[1])
        elif 'lang:' in tag:
            row['lang:'].append(tag.split(':')[1])
        else:
            row['terms_tags'].append(tag)
    return row


def extract_text_from_target(row):
    """
    A function to generate new column for non-null valued 'text_' column
    :param row: Dataframe row
    :return:  New Dataframe row
    """
    if row["text"] != "":
        row["text_"] = row["text"]
    elif "selector" in row["target"][0]:
        row["text_"] = [s["exact"] for s in row["target"][0]["selector"] if
                        s["type"] == "TextQuoteSelector"][0]
    else:
        row["text_"] = ""
    return row


def create_type_columns(row):
    for col in ['is:', 'has:', 'ann:']:
        for val in row[col]:
            row[f"{col.replace(':', '')}_{val}"] = True
    return row


def check_integrity(df):
    # Check if the 'source' field in 'target' column is equal to 'uri'
    data_check = True
    df['target__source'] = df['target'].apply(
        lambda target: target[0]['source'])
    df['source_is_uri'] = df.apply(
        lambda row: row['uri'] == row['target__source'], axis=1)
    if len(df.query('source_is_uri == False')) != 0:
        print("Some sources are not uri")
        data_check = False

    # Check if all values in the column 'id' unique
    if len(df) != len(df['id'].unique()):
        print("Some ids are not unique")
        data_check = False

    # Check if all rows in 'target' column have 'source' field.
    for i in df['target']:
        if i[0]['source'] is None:
            print("Some sources are missing in 'target' column")
            data_check = False

    # Check if 'document' column has only one field 'title'.
    count = 0
    b = 0
    for i in df['document']:
        if i.get("title") is None:
            b = b + 1
        if len(i) > 1:
            count = count + 1
    print(b, ": the number of the documents without title.")
    print(count,
          ": the number of rows that have more than one field in document")

    return data_check


def generate_id(string: str):
    """
    A function to generate id from another column
    :param string:
    :return: hex hash
    """
    return hashlib.sha1(string.encode("utf-8")).hexdigest()


def extract_text_from_document(row):
    """
    # Fill in the 'document' column value from the 'target' column field
     'exact', convert dict -> str
    :param row: dataframe row
    :return: new dataframe row
    """
    if row["document"].get("title"):
        row["document"] = row["document"]["title"][0]
    elif "selector" in row["target"][0]:
        row["document"] = [s["exact"] for s in row["target"][0]["selector"] if
                           s["type"] == "TextQuoteSelector"][0]
    else:
        row["document"] = ""
    return row


def get_ann_by_tag(row, tag_values):
    for tag in tag_values:
        if tag in row['tags']:
            row['date'] = row['text']
        else:
            row['date'] = ""
    return row


def date_format(date):
    if date != "":
        # replace the Nonetype character to empty string.
        date = date.replace('\n', '')
        if len(date) == 4:
            # original format was YYYY
            date = date + "-01-01"
        if len(date) == 7 and date[0] == 0:
            # original format was MM-YYYY
            date = date[3:] + "-" + date[:2] + "-01"
        if len(date) == 7 and date[0] != 0:
            # original format was YYYY-MM
            date = date + "-01"
        if len(date) > 7:
            # original format had another character
            date = date.split(" ", 1)[0]
            if len(date) < 7:
                date = date + "-01-01"
        return date
    else:
        return date


def generate_document(df: pd.DataFrame) -> dict:
    """
    :param df: This dataframe is actually a "grouped-by" dataframe, meaning
    that doc_id, uri, document and tags are the same for all rows
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
        annotation["text"] = row["text_"]
        annotation["tags"] = row["tags"]
        annotation["ann_id"] = row["ann_id"]
        annotation["target"] = row["target"]
        annotation["links"] = row["links"]
        document["annotations"].append(annotation)

    return document


# function to generate the 3rd data format.
def generate_document3(df: pd.DataFrame) -> dict:
    """

    :param df: This dataframe is actually a "grouped-by" dataframe,
    meaning that doc_id, uri, document and tags are the same for all rows
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


def create_and_save_document_es(dataframe):
    documents_es = []

    for doc_id in dataframe['doc_id'].unique():
        sub_df = dataframe.query("doc_id == @doc_id")
        documents_es.append(generate_document3(sub_df))

    tags_to_check = ['has:date', 'has:date-approx']
    dataframe_es = pd.DataFrame(documents_es)
    dataframe_es = dataframe_es.apply(
        lambda row: get_ann_by_tag(row, tags_to_check), axis=1)
    dataframe_es['date'] = dataframe_es['date'].apply(
        lambda date: date_format(date))

    return dataframe_es


def data_cleaning(dataframe):
    print("Cleaning data for ElasticSearch ingestion...")
    dataframe = dataframe.apply(lambda row: extract_text_from_target(row),
                                axis=1)
    dataframe = dataframe.apply(lambda row: extract_text_from_document(row),
                                axis=1)
    dataframe['doc_id'] = dataframe['document'].apply(
        lambda doc: generate_id(doc))
    dataframe = dataframe.rename(columns={'id': 'ann_id'})
    return dataframe


def data_pipeline():
    database = fetch_all_data()
    # Save the fetched database to pickle file
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    database_file = f"./data/hypothesis_database_{now}.pickle"
    database.to_pickle(database_file)
    print(f"Saved latest database to {database_file}")
    database = data_cleaning(database)
    database_es = create_and_save_document_es(database)
    database_es_file = f"./data/hypothesis_database_es_{now}.pickle"
    print(f"Saved cleaned database to {database_es_file}")
    database_es.to_pickle(database_es_file)


if __name__ == '__main__':
    df = pd.read_pickle(r"../data/hypothesis_annotations_20240103_195056")
    df = data_cleaning(df)
    df3 = create_and_save_document_es(df)
