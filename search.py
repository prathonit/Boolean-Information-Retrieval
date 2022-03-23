from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from index import InvertedIndex, PermutermIndex
from crawl import Dataset


def tokenize(s):
    """
    Method to tokenize a string
    :cvar
    """
    i = 0
    length = len(s)
    tokens = []
    temp = ""
    while i < length:
        if s[i] == ' ' or s[i] == '(' or s[i] == ')':
            if len(temp):
                tokens.append(temp)
            if s[i] == '(' or s[i] == ')':
                tokens.append(s[i])
            temp = ""
        else:
            temp += s[i]
        i += 1
    if len(temp):
        tokens.append(temp)
    return tokens


class Postings:
    @staticmethod
    def logical_and(l1, l2):
        """
        Perform logical and of two lists
        :param l1:
        :param l2:
        :return:
        """
        output = []
        i = 0
        j = 0
        len1 = len(l1)
        len2 = len(l2)
        while i < len1 and j < len2:
            if l1[i] == l2[j]:
                output.append(l1[i])
                i += 1
                j += 1
            elif l1[i] < l2[j]:
                i += 1
            else:
                j += 1
        return output

    @staticmethod
    def logical_or(l1, l2):
        """
        Performs logical or of two lists
        :param l1:
        :param l2:
        :return:
        """
        output = []
        hash_map = {}
        for i in l1:
            hash_map[i] = 1
        for i in l2:
            hash_map[i] = 1
        for key in hash_map:
            output.append(key)
        return output


class Parser:
    """
    Parser class parses a search string, retrives the required postings lists and returns the final search result.
    It also performs stop-word removal, stemming and tokenization of the search terms.
    """
    def __init__(self):
        self.ps = PorterStemmer()
        self.look_up = LookUp()
        self.reserved_keywords = ["AND", "OR", "NOT", "(", ")"]

    def pre_process(self, s):
        """
        Removes the stop words, stems and tokenize the tokens
        :param s:
        :return:
        """
        if len(s) and s[0] != '(':
            s = "(" + s + ")"
        tokens = tokenize(s)
        for i in range(len(tokens)):
            if tokens[i] not in self.reserved_keywords:
                tokens[i] = self.ps.stem(tokens[i].lower())
        return tokens

    @staticmethod
    def check_format(tokens):
        """"
        Checks if the format of the query is correct
        :tokens
        """
        tokens_stack = []
        for t in tokens:
            tokens_stack.append(t)
            if tokens_stack[-1] == ")":
                flag = 0
                while len(tokens_stack) and not flag:
                    if tokens_stack[-1] == "(":
                        flag = 1
                    tokens_stack.pop()
                if flag == 0:
                    return False
        return True

    def evaluate_query_terms(self, tokens):
        """
        Evaluate the query terms, replaces the keywords by the posting lists
        :cvar
        """
        evaluated_tokens = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t in self.reserved_keywords:
                if t == "NOT":
                    if i == len(tokens) - 1 or tokens[i+1] in self.reserved_keywords:
                        raise Exception("Not should be followed by a query term")
                    evaluated_tokens.append(self.look_up.query(tokens[i+1], 1))
                    i += 1
                else:
                    evaluated_tokens.append(t)
            else:
                evaluated_tokens.append(self.look_up.query(t))
            i += 1
        return evaluated_tokens

    def parse(self, s):
        """"
        Main method in Parse to parse the query string
        :s
        """
        tokens = self.pre_process(s)
        if not self.check_format(tokens):
            raise Exception("Invalid boolean query")
        tokens = self.evaluate_query_terms(tokens)
        tokens_stack = []
        for t in tokens:
            tokens_stack.append(t)
            if tokens_stack[-1] == ")":
                local_stack = []
                flag = 0
                while len(tokens_stack) and not flag:
                    local_stack.append(tokens_stack[-1])
                    if tokens_stack[-1] == "(":
                        flag = 1
                    tokens_stack.pop()
                if len(local_stack) == 3:
                    tokens_stack.append(local_stack[1])
                else:
                    if local_stack[2] == "AND":
                        tokens_stack.append(Postings.logical_and(local_stack[1], local_stack[3]))
                    else:
                        tokens_stack.append(Postings.logical_or(local_stack[1], local_stack[3]))
        return tokens_stack[0]


class LookUp:
    """"
    LookUp Class
    This class is used to search for a term from inverted index and permuterm index
    It takes care of wildcard characters and also also spelling mistakes by checking the best edit distance terms.
    """
    def __init__(self):
        self.inverted_index = InvertedIndex()
        self.permuterm_index = PermutermIndex()
        self.data_set = Dataset()

    @staticmethod
    def _edit_distance(s1, s2):
        """
        Method to find the edit distance of two strings
        :cvar
        """
        if len(s1) > len(s2):
            s1, s2 = s2, s1
        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    def _get_negation(self, p_list):
        """
        Method to get the negation of a posting list
        :cvar
        """
        output = []
        hash_map = {}
        for i in p_list:
            hash_map[i] = 1
        for key in self.data_set.inverted_file_index:
            if key not in hash_map:
                output.append(key)
        return output

    def _get_qualifying_tokens(self, q):
        """"
        Checks for spelling mistakes, wildcard characters and returns also qualifying posting lists
        :cvar
        """
        output = []
        if q.find('*') != -1:
            # wildcard character
            output = self.permuterm_index.get_tokens(q[q.find('*')+1:] + "$" + q[0:q.find('*')])
        elif not self.permuterm_index.search_token(q + "$"):
            # find closest words using edit distance
            min_ed = 1000000000
            for key in self.inverted_index.index:
                min_ed = min(self._edit_distance(q, key), min_ed)
            for key in self.inverted_index.index:
                ed = self._edit_distance(q, key)
                if ed == min_ed:
                    output.append(key)
            print("Exact term not found for {}".format(q))
            print("Showing results for: {}".format(output))
        else:
            output = [q]
        return output

    def query(self, q, neg=0):
        """
        Returns the posting list for a term.
        Returns negation if neg = 1
        :param q:
        :param neg:
        :return:
        """
        output = []
        tokens = self._get_qualifying_tokens(q)
        for t in tokens:
            postings = self.inverted_index.get_postings(t)
            output = Postings.logical_or(output, postings)
        if neg:
            return self._get_negation(output)
        return output


class Search:
    def __init__(self):
        self.parser = Parser()
        self.data_set = Dataset()

    def find(self, q):
        result = self.parser.parse(q)
        for i in range(len(result)):
            result[i] = self.data_set.inverted_file_index[result[i]]
        return result

