import pickle
from trie import Trie
import config


class PermutermIndex:
    def __init__(self):
        # initialize the index from dump file
        try:
            with open(config.PERMUTERM_INDEX_PATH, "rb") as f:
                self.trie = pickle.load(f)
        except:
            self.trie = Trie()
        self.map = {}

    @staticmethod
    # private helper method to produce string rotations
    def _produce_rotations(s):
        output = []
        # add $ to the end of the string
        s += '$'
        length = len(s)
        for i in range(length):
            temp_s = s[i:] + s[0:i]
            output.append(temp_s)
        return output

    def insert_token(self, t):
        if t not in self.map:
            self.map[t] = 1
            rotations = self._produce_rotations(t)
            for r in rotations:
                self.trie.insert(r)

    def get_tokens(self, prefix):
        return self.trie.get_prefix_words(prefix)

    def save_index(self):
        with open(config.PERMUTERM_INDEX_PATH, "wb") as f:
            pickle.dump(self.trie, f)


class InvertedIndex:
    def __init__(self):
        try:
            with open(config.INVERTED_INDEX_PATH, "rb") as f:
                self.index = pickle.load(f)
        except:
            self.index = {}
        self.map = {}

    def insert_token(self, t, d_id):
        if (t, d_id) not in self.map:
            self.map[(t, d_id)] = 1
            if t not in self.index:
                self.index[t] = []
            i = len(self.index[t]) - 1
            self.index[t].append(d_id)
            while d_id < self.index[t][i]:
                self.index[t][i+1] = self.index[t][i]
                i -= 1
            self.index[t][i+1] = d_id

    def get_postings(self, t):
        if t not in self.index:
            return []
        return self.index[t]

    def save_index(self):
        with open(config.INVERTED_INDEX_PATH, "wb") as f:
            pickle.dump(self.index, f)
