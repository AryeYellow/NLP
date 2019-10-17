from hmm.finalseg.prob_emit import P as emit_P
start_P = {'B': -0.26268660809250016, 'E': -3.14e+100, 'M': -3.14e+100, 'S': -1.4652633398537678}
trans_P = {
    'B': {'E': -0.510825623765990, 'M': -0.916290731874155},
    'E': {'B': -0.5897149736854513, 'S': -0.8085250474669937},
    'M': {'E': -0.33344856811948514, 'M': -1.2603623820268226},
    'S': {'B': -0.7211965654669841, 'S': -0.6658631448798212}
}
PrevStatus = {'B': 'ES', 'M': 'MB', 'S': 'SE', 'E': 'BM'}
MIN_FLOAT = -3.14e100
Force_Split_Words = set()


def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]  # tabular
    path = {}
    for y in states:  # init
        V[0][y] = start_p[y] + emit_p[y].get(obs[0], MIN_FLOAT)
        path[y] = [y]
    for t in range(1, len(obs)):
        V.append({})
        newpath = {}
        for y in states:
            em_p = emit_p[y].get(obs[t], MIN_FLOAT)
            (prob, state) = max(
                [(V[t - 1][y0] + trans_p[y0].get(y, MIN_FLOAT) + em_p, y0) for y0 in PrevStatus[y]])
            V[t][y] = prob
            newpath[y] = path[state] + [y]
        path = newpath

    (prob, state) = max((V[len(obs) - 1][y], y) for y in 'ES')
    return prob, path[state]


def cut_without_dict(sentence):
    prob, pos_list = viterbi(sentence, 'BMES', start_P, trans_P, emit_P)
    begin, nexti = 0, 0
    for i, char in enumerate(sentence):
        pos = pos_list[i]
        if pos == 'B':
            begin = i
        elif pos == 'E':
            yield sentence[begin:i + 1]
            nexti = i + 1
        elif pos == 'S':
            yield char
            nexti = i + 1
    if nexti < len(sentence):
        yield sentence[nexti:]


def cut(sentence):
    for word in cut_without_dict(sentence):
        if word not in Force_Split_Words:
            yield word
        else:
            for c in word:
                yield c


lcut_without_dict = lambda sentence: list(cut_without_dict(sentence))
lcut = lambda sentence: list(cut(sentence))


if __name__ == '__main__':
    text = '柳梦璃C法破阵'
    print('  '.join(cut_without_dict(text)))
    emit_P['B']['C'] = -1
    print('  '.join(cut_without_dict(text)))
    emit_P['S']['梦'] = -1
    print('  '.join(cut(text)))
    Force_Split_Words.add('破阵')
    print('  '.join(cut(text)))
