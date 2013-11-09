from math import log
from itertools import tee

from mrjob.job import MRJob
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

tokenizer = RegexpTokenizer(r'\w+')
common_words = set(stopwords.words('english'))

NUM_DOCS = 3000

class InvalidIDF(Exception):
    pass

class SemicolonValueProtocol(object):
    def write(self, key, values):

        output = [str(key)]

        for v in values:
            output.append(' '.join([str(v[0]), str(v[1])]))

        return ';'.join(output)

class KeyWords(MRJob): 

    OUTPUT_PROTOCOL = SemicolonValueProtocol

    def steps(self):
        return [
            self.mr(mapper=self.unique_words, reducer=self.count_words),
            self.mr(mapper=self.word_to_subs, reducer=self.word_frequencies),
            self.mr(reducer=self.top_words_per_sub)]

    def unique_words(self, key, line):
        line = line.decode('utf-8')
        subreddit_id, text = line.split(',')

        if len(text) > 0 and text[0] == '|':
            text = text[1:-1]

        words = tokenizer.tokenize(text)
        words = map(lambda t: t.lower(), words)
        words = filter(lambda word: len(word) > 2, words)
        unique_words = set(words) - common_words

        for word in unique_words:
            yield subreddit_id, (word, words.count(word))

    def count_words(self, key, words):
        total_words = 0
        word_freq   = dict()

        for word in words:
            text,count = word

            if text not in word_freq:
                word_freq[text] = 0

            word_freq[text] += count
            total_words += count

        yield key, (total_words, word_freq)

    def word_to_subs(self, key, sub_data):
        total, word_freq = sub_data
        subreddit_id = key

        for k,v in word_freq.iteritems():
            yield k, (subreddit_id, v, total)

    def word_frequencies(self, key, values):
        values, values1 = tee(values)
        document_count = sum(map(lambda t: 1, values1))

        idf = log(float(NUM_DOCS) / float(document_count + 1))

        if idf < 0.0:
            raise(InvalidIDF(str(key)))

        for val in values:
            subreddit_id, tf, total = val
            tfidf = tf * idf
            yield subreddit_id, (key, tfidf, total)

    def top_words_per_sub(self, key, values):
        top_words = sorted(values, key=lambda t: t[1], reverse=True)[0:10]
        yield key, top_words

if __name__ == '__main__':
    KeyWords.run()
