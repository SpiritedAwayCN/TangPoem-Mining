import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from sklearn.preprocessing import normalize
from sklearn.preprocessing import Binarizer
from src.poem.constant import word_dict, word_dictr, sim, thresed, poem_tfidf, poems, poem_sim

import config as c

def judge_same_word(str1, str2):
    for c in str1:
        for cc in str2:
            if c == cc:
                return True
    return False

def query_final(key_words, hit=False, author=None):
    syms_list = []
    x_indexes = []
    vals = []
    for word in key_words:
        try:
            wid = word_dict[word]
        except KeyError:
            continue

        syms_list.append(word)
        x_indexes.append(wid)
        vals.append(1)
        
        for sym_id in sim[wid, :].nonzero()[1]:
            sym_word = word_dictr[sym_id]

            if sym_word in key_words:
                continue

            val = sim[wid, sym_id]
            if judge_same_word(word, sym_word) and val > c.sym_thres2:
                syms_list.append(sym_word)
                x_indexes.append(sym_id)
                if c.weight_level1 == 1:
                    vals.append(val)
                else:
                    vals.append(val * (1 if abs(val - 1) < 1e-3 else c.weight_level1))
            elif val > c.sym_thres1:
                syms_list.append(sym_word)
                x_indexes.append(sym_id)
                vals.append(val * c.weight_level2)
    weight_vec = coo_matrix((vals, (x_indexes, [0] * len(vals))), shape=(len(word_dictr), 1)).tocsr()
    res = poem_tfidf * weight_vec  # n x 1
    ret_num = res.data.shape[0]
    res = res.toarray().flatten()
    ans = np.argsort(res)[::-1][:ret_num]
    if not author is None:
        ans = filter(lambda x: poems[x].author == author, ans)
        ans = np.array(list(ans))
    
    if ans.shape[0] == 0:
        return None
    
    if hit == False:
        res = zip(map(lambda x: poems[x], ans), zip(res[ans], [0] * ans.shape[0]))
    else:
        final_poems = set()
        for pid_r in ans:
            for pr in thresed[pid_r, :].nonzero()[1]:
                # ppid = poems[pr].id
                if (not author is None) and poems[pr].author != author:
                    continue
                final_poems.add(pr)

        final_poems = list(final_poems)
        temp = thresed[final_poems, :]
        X = temp[:, final_poems]

        temp = poem_sim[final_poems, :]
        XX = temp[:, final_poems]
        XX = normalize(XX).T

        ans2final = {}
        for i, pid in enumerate(final_poems):
            ans2final[pid] = i

        n = len(final_poems)
        y = np.full((1, n), 1)
        y = csr_matrix(y)
        new_y = np.zeros((1, n))
        if n > 0:
            last_y = csr_matrix(np.zeros((1, n)))
            for i in range(70):
                new_y = normalize(y)
                dis = np.sum((new_y - last_y).toarray()**2)
                # print(i, dis)
                if  np.sqrt(dis) <= 1e-3:
                    break
                last_y = new_y
                y = new_y * X
        
        # idx = []
        # for i in ans:
        #     idx.append(ans2final[i])
        new_y = new_y * XX

        idx = list(map(lambda x: ans2final[x], ans))
        # print(max(ans2final.values()), max(idx))

        res = zip(map(lambda x: poems[x], ans), zip(res[ans], new_y.toarray().flatten()[idx]))

    res = list(res)
    if c.show_sym_list:
        print(syms_list)

    if c.debug_mode:
        for entry in res:
            print(entry)

    return set(syms_list), res

def main(*argv, **args):
    sym_list, res = query_final(*argv, **args)
    print(sym_list)
    for entry in res:
        print(entry)

if __name__ == '__main__':
    main(['明月'], hit=True)