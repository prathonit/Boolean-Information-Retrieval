import os
import pickle
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from index import InvertedIndex, PermutermIndex
import config


class Dataset:
    """
    Dataset class
    This class handles the information source and is responsible for loading the required text files.
    It assigns a unique docID (d_id) to each document for easier reference.
    It also creates a reverse index to get the document from doc_id efficiently
    The indexes are stored in a .pk file for later usage
    """
    def __init__(self):
        fs = os.listdir(config.DATASET_PATH)
        self.file_list = []
        for f in fs:
            if f.endswith(".txt"):
                self.file_list.append(f)
        # assigning a unique id to each file
        # fetching file index
        self.file_index = {}
        self.inverted_file_index = {}
        self.file_count = 0
        self.load_file_index()
        self.update_file_index()
        self.save_file_index()
        for key, value in self.file_index.items():
            self.inverted_file_index[value] = key

    def load_file_index(self):
        try:
            with open(config.FILE_INDEX_PATH, "rb") as f:
                fi = pickle.load(f)
                self.file_index = fi
                self.file_count = len(self.file_index)
        except:
            print("Failed to load file index from {}".format(config.FILE_INDEX_PATH))

    def update_file_index(self):
        for file in self.file_list:
            if file not in self.file_index:
                self.file_index[file] = self.file_count
                self.file_count += 1

    def save_file_index(self):
        with open(config.FILE_INDEX_PATH, "wb") as f:
            pickle.dump(self.file_index, f)


class Preprocessor:
    """
    Preprocessor class
    This class helps in processing the dataset input.
    It removes the stopwords, applies stemming to words and converts the words to lower case.
    """
    def __init__(self):
        self.stop_words = stopwords.words("english")
        self.ps = PorterStemmer()
        self.tokenizer = RegexpTokenizer(r"\w+")

    def process(self, file):
        try:
            with open(os.path.join(config.DATASET_PATH, file)) as f:
                tokens = []
                lines = f.readlines()
                for line in lines:
                    w = self.tokenizer.tokenize(line)
                    w = [x.lower() for x in w]
                    w = self.remove_stopwords(self.stop_words, w)
                    self.stem_words(w)
                    tokens.extend(w)
                return tokens
        except:
            print("Failed to read {}".format(file))
            return []

    @staticmethod
    def remove_stopwords(stop_words, words):
        output = []
        for word in words:
            if word not in stop_words:
                output.append(word)
        return output

    def stem_words(self, words):
        for i in range(len(words)):
            words[i] = self.ps.stem(words[i])


class Crawler:
    """
    Crawler Class
    Crawler class makes use of Dataset class and Preprocessor class to generate the index.
    It visits each document provided by the Dataset class and Pre-Processes those using PreProcessor class
    Then it adds the tokens to PermutermIndex and InvertedIndex
    """
    def __init__(self):
        self.data_set = Dataset()
        self.pre_processor = Preprocessor()
        self.inverted_index = InvertedIndex()
        self.permuterm_index = PermutermIndex()

    def process(self):
        i = 1
        for file in self.data_set.file_list:
            print("{} out of {}".format(i, len(self.data_set.file_list)))
            tokens = self.pre_processor.process(file)
            for t in tokens:
                self.inverted_index.insert_token(t, self.data_set.file_index[file])
                self.permuterm_index.insert_token(t + "$")
            i += 1
        self.inverted_index.save_index()
        self.permuterm_index.save_index()