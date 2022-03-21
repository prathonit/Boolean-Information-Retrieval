import os
import pickle
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from index import InvertedIndex, PermutermIndex
import config

ps = PorterStemmer()


class Dataset:
    def __init__(self):
        self.file_list = os.listdir(config.DATASET_PATH)
        # assigning a unique id to each file
        # fetching file index
        self.file_index = {}
        self.file_count = 0
        self.load_file_index()
        self.update_file_index()
        self.save_file_index()

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
    def __init__(self):
        self.stop_words = stopwords.words('english')

    def process(self, file):
        try:
            with open(os.path.join(config.DATASET_PATH, file)) as f:
                tokens = []
                lines = f.readlines()
                for line in lines:
                    w = word_tokenize(line)
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

    @staticmethod
    def stem_words(words):
        for i in range(len(words)):
            words[i] = ps.stem(words[i])


class Crawler:
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
                self.permuterm_index.insert_token(t)
            i += 1
        self.inverted_index.save_index()
        self.permuterm_index.save_index()


c = Crawler()
c.process()
print("Finished")