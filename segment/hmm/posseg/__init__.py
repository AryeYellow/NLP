from hmm import tokenizer, X
from hmm.posseg.char_state_tab import P as char_state_tab_P
from hmm.posseg.prob_start import P as start_P
from hmm.posseg.prob_trans import P as trans_P
from hmm.posseg.prob_emit import P as emit_P

MIN_FLOAT = -3.14e100
MIN_INF = float('-inf')


class Word:
    def __init__(self, word, flag):
        self.word = word
        self.flag = flag

    def __repr__(self):
        return '%s %s' % (self.word, self.flag)

    def __str__(self):
        return self.word


def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]  # tabular
    mem_path = [{}]
    all_states = trans_p.keys()
    for y in states.get(obs[0], all_states):  # init
        V[0][y] = start_p[y] + emit_p[y].get(obs[0], MIN_FLOAT)
        mem_path[0][y] = ''
    for t in range(1, len(obs)):
        V.append({})
        mem_path.append({})

        prev_states = [x for x in mem_path[t - 1].keys() if len(trans_p[x]) > 0]

        prev_states_expect_next = set(
            (y for x in prev_states for y in trans_p[x].keys()))
        obs_states = set(
            states.get(obs[t], all_states)) & prev_states_expect_next

        if not obs_states:
            obs_states = prev_states_expect_next if prev_states_expect_next else all_states

        for y in obs_states:
            prob, state = max((V[t - 1][y0] + trans_p[y0].get(y, MIN_INF) +
                               emit_p[y].get(obs[t], MIN_FLOAT), y0) for y0 in prev_states)
            V[t][y] = prob
            mem_path[t][y] = state

    last = [(V[-1][y], y) for y in mem_path[-1].keys()]

    prob, state = max(last)

    route = [None] * len(obs)
    i = len(obs) - 1
    while i >= 0:
        route[i] = state
        state = mem_path[i][state]
        i -= 1
    return prob, route


def cut_without_dict(sentence):
    prob, pos_list = viterbi(sentence, char_state_tab_P, start_P, trans_P, emit_P)
    begin, nexti = 0, 0
    for i, char in enumerate(sentence):
        pos = pos_list[i][0]
        if pos == 'B':
            begin = i
        elif pos == 'E':
            yield Word(sentence[begin:i + 1], pos_list[i][1])
            nexti = i + 1
        elif pos == 'S':
            yield Word(char, pos_list[i][1])
            nexti = i + 1
    if nexti < len(sentence):
        yield Word(sentence[nexti:], pos_list[nexti][1])


class POSTokenizer:

    def __init__(self):
        self.tokenizer = tokenizer
        self.word2flag = self.tokenizer.word2flag

    def cut(self, sentence):
        route = self.tokenizer.calculate(sentence)
        x = 0
        buf = ''
        N = len(sentence)
        while x < N:
            y = route[x][1] + 1
            l_word = sentence[x:y]
            if y - x == 1:
                buf += l_word
            else:
                if buf:
                    if len(buf) == 1:
                        yield Word(buf, self.word2flag.get(buf, X))
                    else:
                        for t in cut_without_dict(buf):  # HMM
                            yield t
                    buf = ''
                yield Word(l_word, self.word2flag.get(l_word, X))
            x = y
        if buf:
            if len(buf) == 1:
                yield Word(buf, self.word2flag.get(buf, X))
            else:
                for t in cut_without_dict(buf):
                    yield t

    def lcut(self, sentence):
        return list(self.cut(sentence))

    def cut_without_hmm(self, sentence):
        for word in self.tokenizer.cut_without_hmm(sentence):
            yield Word(word, self.word2flag.get(word, X))

    def lcut_without_hmm(self, sentence):
        return list(self.cut_without_hmm(sentence))


tk = POSTokenizer()
cut = tk.cut
lcut = tk.lcut
cut_without_hmm = tk.cut_without_hmm
lcut_without_hmm = tk.lcut_without_hmm


if __name__ == '__main__':
    text = '柳梦璃施法入梦'
    print(list(cut_without_dict(text)))
    emit_P[('E', 'v')]['梦'] = -1
    print(list(cut_without_dict(text)))

