
def levenshteinDistance(s1, s2):
    x = {}
    fill_memo_table(len(s1) - 1, len(s2) - 1, s1, s2, x)
    return x[(len(s1) - 1, len(s2) - 1)]


def fill_memo_table(i, j, s1, s2, x):
    if x.get((i, j), -1) == -1:
        if i == 0:
            x[(i, j)] = j
        elif j == 0:
            x[(i, j)] = i
        elif s1[i] == s2[j]:
            x[(i, j)] = fill_memo_table(i-1, j-1, s1, s2, x)
        else:
            x[(i, j)] = 1 + min(fill_memo_table(i-1, j-1, s1, s2, x),
                                fill_memo_table(i, j-1, s1, s2, x),
                                fill_memo_table(i-1, j, s1, s2, x))
    return x[(i, j)]
