class TrieNode:
    def __init__(self):
        self.children = dict()
        self.is_eow = False


class Trie:
    def __init__(self):
        self.root = self.get_node()

    @staticmethod
    def get_node():
        return TrieNode()

    def insert(self, s):
        current_root = self.root
        length = len(s)
        for i in range(length):
            if s[i] not in current_root.children:
                current_root.children[s[i]] = self.get_node()
            current_root = current_root.children[s[i]]
        current_root.is_eow = True

    def search(self, s):
        current_root = self.root
        length = len(s)
        for i in range(length):
            if s[i] not in current_root.children:
                return False
            current_root = current_root.children[s[i]]

        return current_root.is_eow

    def _get_end_node(self, s):
        current_root = self.root
        length = len(s)
        for i in range(length):
            current_root = current_root.children[s[i]]
        return current_root

    def _get_all_prefix_words(self, prefix, prefix_words, current_node):
        if current_node and current_node.is_eow:
            prefix_words.append(prefix)
        for key in current_node.children:
            current_char = key
            self._get_all_prefix_words(prefix + current_char, prefix_words, current_node.children[key])

    def get_prefix_words(self, prefix):
        prefix_end_node = self._get_end_node(prefix)
        output = []
        self._get_all_prefix_words(prefix, output, prefix_end_node)
        return output
