import datetime
import sys

from modules.data_pipeline import *
from tabulate import tabulate
from modules.es_ingestion import *
from modules.search import *


def main():
    if len(list(Path(r"data").glob("*database_es*.pickle"))) == 0:
        print("No database detected. Fetching data from Hypothes.is...")
        data_pipeline()
    database_file = list(Path(r"data").glob("*document_es*.pickle"))[-1]
    creation_time = datetime.datetime. \
        fromtimestamp(database_file.stat().st_ctime). \
        isoformat(sep=" ", timespec="seconds")

    database_df = pd.read_pickle(database_file)

    while True:
        i = 1
        print(f"{i} - Search Database")
        print(f"{i+1} - Review database")
        print(f"{i+2} - Update database")
        print(f"{i+3} - Quit")
        selection = input("Select option: ")
        if selection == str(i):
            es = es_ingestion(database_df)
            print("1 - Search by ID")
            print("2 - Search by tag")
            print("3 - Quit")
            search = input("Select: ")
            if search == "1":
                search_keyword = input("Enter ID to search:")
                response = search_id(es, search_keyword)
                print(response)
            elif search == "2":
                search_keyword = input("Enter tag to search:")
                response = search_tag(es, list(search_keyword))
                print(response)
            elif search == "3":
                sys.exit()
            else:
                print("Invalid input.")
        elif selection == str(i+1):
            print(tabulate(
                [[str(database_file.name), len(database_df), creation_time]],
                headers=["Database", "Entries", "Updated"],
                tablefmt="grid"
            ))
        elif selection == str(i+2):
            check_database_update()
        elif selection == str(i+3):
            sys.exit()
        else:
            print(f"Invalid input")


if __name__ == '__main__':
    main()
    # check_database_update()
