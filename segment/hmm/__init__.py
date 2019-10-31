from os import path
import re
from math import log
from hmm import finalseg
fname = path.join(path.dirname(__file__), 'dict.txt')
X = 'X'


class Tokenizer:
    re_eng = re.compile('[a-zA-Z]+')
    re_m = re.compile('[+-]?([0-9]+|[0-9]+[./~-][0-9]+)[%π]?')  # jieba数词标注为m

    def __init__(self, word2freq, total, word2flag, max_len=16):
        self.word2freq = word2freq
        self.total = total
        self.word2flag = word2flag
        self.max_len = max_len

    @classmethod
    def initialize(cls):
        word2freq, total, word2flag = dict(), 0, dict()
        with open(fname, encoding='utf-8') as f:
            for line in f.read().strip().split('\n'):
                word, freq, flag = line.split()
                freq = int(freq)
                word2freq[word] = freq
                total += freq
                word2flag[word] = flag
        # 词最大长度，默认等于词典最长词（超长英文符会识别不出来）
        max_len = max(len(i) for i in word2freq.keys())
        return cls(word2freq, total, word2flag, max_len)

    def get_DAG(self, sentence):
        length = len(sentence)
        DAG = dict()
        for head in range(length):
            tail = min(head + self.max_len, length)
            DAG.update({head: [head]})
            for middle in range(head + 2, tail + 1):
                word = sentence[head: middle]
                if word in self.word2freq:
                    DAG[head].append(middle - 1)
                # ------------- 正则 ------------- #
                elif self.re_eng.fullmatch(word):
                    DAG[head].append(middle - 1)
                elif self.re_m.fullmatch(word):
                    DAG[head].append(middle - 1)
        return DAG

    def calculate(self, sentence):
        DAG = self.get_DAG(sentence)
        length = len(sentence)
        route = dict()
        route[length] = (0, 0)
        logtotal = log(self.total)
        for idx in range(length - 1, -1, -1):
            route[idx] = max(
                (log(self.word2freq.get(sentence[idx:x + 1], 1)) - logtotal + route[x + 1][0], x)
                for x in DAG[idx])
        return route

    def cut(self, sentence):
        route = self.calculate(sentence)
        length = len(sentence)
        x = 0
        buf = ''
        while x < length:
            y = route[x][1] + 1
            l_word = sentence[x:y]
            if y - x == 1:
                buf += l_word
            else:
                if buf:
                    if len(buf) == 1:
                        yield buf
                        buf = ''
                    else:
                        for t in finalseg.cut(buf):
                            yield t
                        buf = ''
                yield l_word
            x = y
        if buf:
            if len(buf) == 1:
                yield buf
            else:
                for t in finalseg.cut(buf):
                    yield t

    def cut_without_hmm(self, sentence):
        route = self.calculate(sentence)
        length = len(sentence)
        x = 0
        while x < length:
            y = route[x][1] + 1
            l_word = sentence[x:y]
            yield l_word
            x = y

    def lcut(self, sentence):
        return list(self.cut(sentence))

    def add_word(self, word, freq=0, flag=X):
        if freq > 0:
            self.del_word(word)
        else:
            freq = 1
        original_freq = self.word2freq.get(word, 0)
        self.word2freq[word] = original_freq + freq
        self.total = self.total - original_freq + self.word2freq[word]
        self.word2flag[word] = flag

    def del_word(self, word):
        finalseg.Force_Split_Words.add(word)  # 强制拆词
        original_freq = self.word2freq.get(word)
        if original_freq is not None:
            del self.word2freq[word]
            self.total -= original_freq
            del self.word2flag[word]


# 实例化
tokenizer = Tokenizer.initialize()
cut = tokenizer.cut
lcut = tokenizer.lcut
add_word = tokenizer.add_word
del_word = tokenizer.del_word
cut_without_hmm = tokenizer.cut_without_hmm


if __name__ == '__main__':
    text = '柳梦璃施法dream-01食梦'
    print('  '.join(cut_without_hmm(text)))
    print('  '.join(cut(text)))
    add_word('dream-01')
    add_word('梦璃', flag='nr')
    del_word('食梦')
    print('  '.join(cut(text)))
    print(tokenizer.word2freq['梦璃'])
