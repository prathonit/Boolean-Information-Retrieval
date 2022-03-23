import pickle
from trie import Trie
import config


class PermutermIndex:
    """
    PermutermIndex class
    PermutermIndex is used to store the available keywords in our index
    It stores all the rotations of a given keyword
    For eg,
    hello  => $hello ello$h llo$h and so on
    In case of a wildcard query we can then utilize this index to get the matching keywords
    For eg for query: hel*o
    we can search for o$hel in the PermutermIndex
    """
    def __init__(self):
        # initialize the index from dump file
        try:
            with open(config.PERMUTERM_INDEX_PATH, "rb") as f:
                self.trie = pickle.load(f)
        except:
            self.trie = Trie()
        self.map = {}

    @staticmethod
    def _fix_rotation(s):
        """
        :cvar
        """
        return s[s.find("$")+1:]+s[0:s.find("$")]

    @staticmethod
    # private helper method to produce string rotations
    def _produce_rotations(s):
        """
        Produce all rotations of a string
        :param s:
        :return:
        """
        output = []
        length = len(s)
        for i in range(length):
            temp_s = s[i:] + s[0:i]
            output.append(temp_s)
        return output

    def insert_token(self, t):
        """
        Insert a token into the trie with all the rotations
        :cvar
        """
        if t not in self.map:
            self.map[t] = 1
            rotations = self._produce_rotations(t)
            for r in rotations:
                self.trie.insert(r)

    def get_tokens(self, prefix):
        """
        Get all tokens with certain prefix
        :cvar
        """
        output = self.trie.get_prefix_words(prefix)
        for i in range(len(output)):
            output[i] = self._fix_rotation(output[i])
        return output

    def search_token(self, t):
        """
        Check if a token is present in the trie
        :cvar
        """
        return self.trie.search(t)

    def save_index(self):
        with open(config.PERMUTERM_INDEX_PATH, "wb") as f:
            pickle.dump(self.trie, f)


class InvertedIndex:
    """
    InvertedIndex class
    InvertedIndex is used to store the mapping form keywords to doc_id
    It generates posting lists for each keyword, each posting list has ids of the documents which contain the specific
    keyword
    """
    def __init__(self):
        try:
            with open(config.INVERTED_INDEX_PATH, "rb") as f:
                self.index = pickle.load(f)
        except:
            self.index = {}

    def insert_token(self, t, d_id):
        """
        Insert a token in the inverted index
        :param t:
        :param d_id:
        :return: None
        """
        if t not in self.index:
            self.index[t] = []
        i = len(self.index[t]) - 1
        self.index[t].append(d_id)
        while d_id < self.index[t][i]:
            self.index[t][i+1] = self.index[t][i]
            i -= 1
        if i >= 0 and self.index[t][i] != d_id:
            self.index[t][i+1] = d_id

    def get_postings(self, t):
        """
        Get the postings for a keyword
        :param t:
        :return:
        """
        if t not in self.index:
            return []
        return self.index[t]

    def save_index(self):
        """
        Save the index into the .pk for later retrieval
        :cvar
        """
        with open(config.INVERTED_INDEX_PATH, "wb") as f:
            pickle.dump(self.index, f)
