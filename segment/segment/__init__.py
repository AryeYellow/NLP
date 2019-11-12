from re import compile
from math import log
from segment.corpus import txt2df, df2dt

RE_EN = compile('[a-zA-Z]+')
RE_NUM = compile('[0-9]+%?|[0-9]+[.][0-9]+%?')
NA, EN, NUM = 'NA', 'EN', 'NUM'
GET_FREQ = lambda w: {1: 2000, 2: 300, 3: 40, 4: 5}.get(len(w), 2)


class Tokenizer:

    def __init__(self, word2freq, word2flag):
        self.word2freq = word2freq
        self.total = sum(word2freq.values())
        self.max_len = max(len(i) for i in word2freq.keys())  # 词最大长度
        self.word2flag = word2flag
        self.re_ls = [RE_EN, RE_NUM]  # 正则表达式匹配
        self.re_flags = [EN, NUM]

    @classmethod
    def initialize(cls):
        df = txt2df()
        word2freq = df2dt(df[[0, 1]])
        word2flag = df2dt(df[[0, 2]])
        return cls(word2freq, word2flag)

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
                    continue
                for r in self.re_ls:
                    if r.fullmatch(word):
                        DAG[head].append(middle - 1)
                        break
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
        while x < length:
            y = route[x][1] + 1
            l_word = sentence[x:y]
            yield l_word
            x = y

    def lcut(self, sentence):
        return list(self.cut(sentence))

    def add_word(self, word, freq=-1, flag=None, add=True):
        original_freq = self.word2freq.get(word, 0)
        freq = GET_FREQ(word) if freq < 0 else freq
        self.word2freq[word] = original_freq + freq if add else freq
        self.total = self.total - original_freq + self.word2freq[word]
        self.word2flag[word] = flag if flag else self.get_flag(word)

    def del_word(self, word):
        original_freq = self.word2freq.get(word)
        if original_freq is not None:
            del self.word2freq[word]
            self.total -= original_freq
            del self.word2flag[word]

    def update_dt(self, word2freq, word2flag):
        self.word2freq.update(word2freq)
        self.total = sum(word2freq.values())
        self.max_len = max(len(i) for i in word2freq.keys())  # 词最大长度
        self.word2flag = dict(word2flag, **self.word2flag)

    def get_flag(self, word):
        if word in self.word2flag:
            return self.word2flag[word]
        for r, flag in zip(self.re_ls, self.re_flags):
            if r.fullmatch(word):
                return flag
        return NA

    def get_flags(self, words):
        return [self.get_flag(word) for word in words]

    def add_re(self, re_ls, re_flags, max_len):
        self.re_ls.extend(re_ls)
        self.re_flags.extend(re_flags)
        self.max_len = max_len


class Tk(Tokenizer):

    def cut_with_position(self, sentence):
        route = self.calculate(sentence)
        length = len(sentence)
        x = 0
        while x < length:
            y = route[x][1] + 1
            l_word = sentence[x:y]
            yield l_word, x, y
            x = y

    def highlight(self, sentence, word, half=32):
        red = '\033[031m%s\033[0m' % word
        for l_word, x, y in self.cut_with_position(sentence):
            if l_word == word:
                print(sentence[max(0, x-half):x] + red + sentence[y:y+half])

    def highlight_re(self, sentence, pattern, half=32):
        self.re_ls.append(compile(pattern) if isinstance(pattern, str) else pattern)
        for l_word, x, y in self.cut_with_position(sentence):
            if self.re_ls[-1].fullmatch(l_word):
                word = '\033[031m%s\033[0m' % l_word
                print(sentence[max(0, x-half):x] + word + sentence[y:y+half])
        print(self.re_ls.pop())

    def highlight_yield(self, sentence, word_set, wrap='【%s】', length=85):
        word_set = {word_set} if isinstance(word_set, str) else word_set
        half = (length - max(len(w) for w in word_set)) // 2 - 1
        s = sentence.replace('【', ' ').replace('】', ' ')
        for l_word, x, y in self.cut_with_position(s):
            if l_word in word_set:
                yield l_word, s[max(0, x-half):x] + wrap % l_word + s[y:y+half]


# 实例化
tk = Tk.initialize()
cut = tk.cut
lcut = tk.lcut
add_word = tk.add_word
del_word = tk.del_word
get_flag = tk.get_flag
get_flags = tk.get_flags
cut_with_position = tk.cut_with_position
highlight = tk.highlight
highlight_re = tk.highlight_re


if __name__ == '__main__':
    text = 'Blade Master斩杀大法师'
    print(lcut(text))
    add_word('Blade Master', 2, 'HERO')
    add_word('法师', 10**10)
    print(lcut(text))
    print(get_flags(cut('Blade Master斩杀Archmage')))
    print(tk.word2freq.get('法师'))
    tk.highlight_re(text, '[a-z A-Z]+', 1)
