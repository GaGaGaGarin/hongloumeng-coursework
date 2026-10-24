# -*- coding: utf-8 -*-
"""
作业2：信息论与自然语言处理
基于语料库计算：信息熵、共同词典概率分布、KL 散度、交叉熵、点互信息矩阵。

用法：直接运行  python homework.py
说明：语料为已分词文本（词与词以空格分隔，句与句以换行分隔）。
"""

import math
import os

# ---------- 0. 读取语料库 ----------
# 注意：原 notebook 中是服务器路径 /data/bigfiles/...，已改成本地 data/ 目录。
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def read_corpus(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return f.read().strip()


yuwen = read_corpus("yuwen.txt")
hsk = read_corpus("hsk.txt")
children = read_corpus("children.txt")
news = read_corpus("news.txt")


# ---------- 1. 统计词频 ----------
def get_wordfreq(text):
    """统计词频，返回 {词: 频次}。"""
    word_counts = {}
    for word in text.split(" "):
        word_counts[word] = word_counts.get(word, 0) + 1
    return word_counts


# ---------- 2. 计算语料库信息熵 ----------
def text_entropy(text):
    """以词为符号单元，计算文本的信息熵（单位 bit）。"""
    word_freq = get_wordfreq(text)
    total_words = sum(word_freq.values())
    entropy = 0.0
    for freq in word_freq.values():
        p = freq / total_words
        entropy -= p * math.log2(p)
    print(f"词数：{total_words:d}，信息熵: {entropy:.4f} bits")
    return entropy


# ---------- 3. 两个语料库共同词典的概率分布 ----------
def commWordProb(text1, text2):
    """取两个语料库共同出现的词，分别计算其概率，返回两个等长概率列表。"""
    freq1 = get_wordfreq(text1)
    freq2 = get_wordfreq(text2)
    total1 = sum(freq1.values())
    total2 = sum(freq2.values())

    common_words = set(freq1.keys()) & set(freq2.keys())
    prob1, prob2 = [], []
    for w in common_words:
        prob1.append(freq1[w] / total1)
        prob2.append(freq2[w] / total2)
    print(f"共同词典大小：{len(common_words)}")
    return prob1, prob2


# ---------- 4. KL 散度与交叉熵 ----------
def KL(prob1, prob2):
    """KL(p||q) = Σ p·log2(p/q)，只对 p>0 且 q>0 的项求和。"""
    kl = 0.0
    for p, q in zip(prob1, prob2):
        if p > 0 and q > 0:
            kl += p * math.log2(p / q)
    print("相对熵 KL(p||q)：", round(kl, 6))
    return kl


def crossEntropy(prob1, prob2):
    """交叉熵 H(p,q) = -Σ p·log2(q)。"""
    cross_entropy = 0.0
    for p, q in zip(prob1, prob2):
        if p > 0 and q > 0:
            cross_entropy -= p * math.log2(q)
    print("交叉熵 H(p,q)：", round(cross_entropy, 6))
    return cross_entropy


# ---------- 5. 点互信息矩阵 ----------
STOP_WORDS = ["《", "》", "，", "。", "“", "”", "；", "、", "（", "）", "！", "：",
              "的", "着", "了", "？", "吗", "得", "而", "但", "并", "但是", "是",
              "在", "这", "\n"]


def gen_pmi_matrix(text, word_frequency_threshold):
    """生成点互信息矩阵，返回 {(w1, w2): pmi}。

    PMI(w1,w2) = log2( P(w1,w2) / (P(w1)·P(w2)) )
    其中共现 P(w1,w2) 用“同一句中出现”近似，即 共现句数 / 总句数。
    """
    sentence_list = text.split("\n")
    word_list = text.split(" ")
    total_words = len(word_list)
    sent_num = len(sentence_list)

    word_freq = get_wordfreq(text)

    # 过滤低频词和停用词
    filtered_words = [
        w for w, f in word_freq.items()
        if f > word_frequency_threshold and w not in STOP_WORDS
    ]
    print("过滤后词表大小：", len(filtered_words))
    filtered_set = set(filtered_words)

    # 词概率
    word_prob = {w: word_freq[w] / total_words for w in filtered_words}

    # 统计共现：同一句中出现即共现一次（无序词对，保证 w1 < w2）
    cooccur = {}
    for sentence in sentence_list:
        words_in_sentence = set(sentence.split(" ")) & filtered_set
        if len(words_in_sentence) < 2:
            continue
        word_list_local = sorted(words_in_sentence)
        n = len(word_list_local)
        for i in range(n):
            wi = word_list_local[i]
            for j in range(i + 1, n):
                wj = word_list_local[j]
                cooccur[(wi, wj)] = cooccur.get((wi, wj), 0) + 1

    # 计算 PMI
    pmi_matrix = {}
    for (w1, w2), cnt in cooccur.items():
        p_joint = cnt / sent_num
        pmi = math.log2(p_joint / (word_prob[w1] * word_prob[w2]))
        pmi_matrix[(w1, w2)] = pmi

    print("共现词对数：", len(pmi_matrix))
    return pmi_matrix


# ---------- 6. 查询互信息矩阵 ----------
def search_pmi(word, pmi_matrix):
    """查询与某词共现的 PMI，按 PMI 从大到小排序。"""
    result = []
    for (w1, w2), pmi in pmi_matrix.items():
        if word == w1:
            result.append(((w1, w2), pmi))
        elif word == w2:
            result.append(((w1, w2), pmi))
    result.sort(key=lambda kv: (kv[1], kv[0]), reverse=True)
    print(f"与『{word}』共现的 PMI 前 15：")
    for (pair, pmi) in result[:15]:
        other = pair[1] if pair[0] == word else pair[0]
        print(f"  {word} -- {other}: {pmi:.4f}")
    return result


# ---------- 主流程 ----------
if __name__ == "__main__":
    print("=" * 60)
    print("一、各语料库信息熵")
    print("=" * 60)
    for name, corpus in [("hsk", hsk), ("yuwen", yuwen),
                         ("children", children), ("news", news)]:
        print(f"[{name}] ", end="")
        text_entropy(corpus)

    print("\n" + "=" * 60)
    print("二、两两语料库的 KL 散度与交叉熵")
    print("=" * 60)
    corpus_map = {"hsk": hsk, "yuwen": yuwen, "children": children, "news": news}
    pairs = [("hsk", "yuwen"), ("hsk", "news"),
             ("yuwen", "children"), ("children", "news")]
    for a, b in pairs:
        print(f"\n--- {a} vs {b} ---")
        p1, p2 = commWordProb(corpus_map[a], corpus_map[b])
        KL(p1, p2)
        crossEntropy(p1, p2)
        # 反向 KL，用于展示 KL 的不对称性
        p2_, p1_ = commWordProb(corpus_map[b], corpus_map[a])
        print(f"反向 KL({b}||{a})：", round(KL(p2_, p1_), 6))

    print("\n" + "=" * 60)
    print("三、点互信息矩阵（以 news 语料、阈值 50 为例）")
    print("=" * 60)
    m = gen_pmi_matrix(news, 50)
    search_pmi("中国", m)
    search_pmi("市场", m)
