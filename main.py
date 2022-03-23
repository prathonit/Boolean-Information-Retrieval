import time
import argparse
from crawl import Crawler, Preprocessor
from search import Search
from nltk.corpus import stopwords

"""
This program is a boolean information retrieval system.
Usage instructions:
Run:
python main.py --index --search
--index = To index the dataset
--search = To search the dataset
"""


def print_perf_time(t, op_name="Operation"):
    """ To print the execution time for a process """
    t_ms = t / 1000000
    t_s = t_ms / 1000
    print("{} took {} ms or {} seconds".format(op_name, t_ms, t_s))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", help="index the dataset", action="store_true")
    parser.add_argument("--search", help="search the dataset", action="store_true")

    parser.add_argument("--stopword", help="Eg stopword", action="store_true")
    parser.add_argument("--stemming", help="Eg stemming", action="store_true")
    parser.add_argument("--query", help="Eg query", action="store_true")
    args = parser.parse_args()
    if args.index:
        """ use --index flag to index the dataset """
        start = time.perf_counter_ns()
        c = Crawler()
        c.process()
        end = time.perf_counter_ns()
        print_perf_time(end - start, "Indexing operation")
    if args.search:
        """ use --- search flag to search the dataset """
        search = Search()
        search_expr = input("Enter the search expression: ")
        while search_expr.lower() != "exit":
            start = time.perf_counter_ns()
            result = search.find(search_expr)
            end = time.perf_counter_ns()
            print("Found {} results in {} ms".format(len(result), (end - start) / 1000000))
            print(result)
            print_perf_time(end - start, "Search operation")
            search_expr = input("Enter the search expression: ")
    if args.stopword:
        sw = stopwords.words("english")
        print(Preprocessor.remove_stopwords(sw, ["This", "is", "an", "apple"]))
    if args.stemming:
        p = Preprocessor()
        li = ["This", "is", "an", "apple"]
        p.stem_words(li)
        print(li)
    if args.query:
        search = Search()
        print("Result")
        print(search.find("(MACBETH OR JULIUS)"))


if __name__ == "__main__":
    main()
