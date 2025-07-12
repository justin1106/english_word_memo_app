import requests
import random
# from pprint import pprint
from pocketbase import PocketBase
import config

base_url = config.POCKETBASE_URL

client = PocketBase(config.POCKETBASE_URL)
# api = "/api/collections/cw_english_words/records"
# url = base_url + api


total_word = 2995


def get_all_word(collection_name, page):
    # url = base_url + f'/api/collections/{collection_name}/records'
    # result = client.collection(collection_name).get_list()
    per_page = 30
    wordslist = client.collection(collection_name).get_list(page, per_page).items
    return wordslist


def get_words(word_all):
    word_all = word_all.copy()
    # print(len(word_all))
    # 전체 30개, 틀린단어(복습단어) 최소 25%
    # 1. 필터를 사용해서 틀린단어만 전체 가져오기 => 중복가능성, 중복안되게 set()
    # 2. 1의 갯수가 전체의 25% 갯수보다 큰지 확인
    # 3. 복습단어 25% 갯수 뽑기
    # 4. word_all에서 복습단어 제외하기
    # 5. word_all에서 75% 갯수 뽑기
    # 6. 새단어묶음으로 만들기
    # 7. 새단어묶음 섞기
    wrong_results = (
        client.collection("cw_english_words_results")
        .get_list(query_params={"filter": "iscorrect = False"})
        .items
    )
    all_results = client.collection("cw_english_words_results").get_list().items

    results = []
    for a in all_results:
        results.append(a.en_word_id)
    wrong_words = []
    for r in wrong_results:
        wrong_words.append(r.en_word_id)
    wrong_words = set(wrong_words)
    # pprint(wrong_words)

    word_num = len(wrong_words)
    # print(word_num)
    random_word = []
    if word_num < 5:
        for w in wrong_words:
            random_word.append(client.collection("cw_english_words").get_one(w))
    if word_num >= 5:
        for i in range(5):
            w_index = random.randint(0, len(wrong_words) - i - 1)
            word = client.collection("cw_english_words").get_one(
                list(wrong_words)[w_index]
            )
            random_word.append(word)
        word_num = 5
    for r in results:
        for w in word_all:
            if w.id == r:
                word_all.remove(w)
    # pprint(word_all)
    for i in range(10 - word_num):
        w_index = random.randint(0, len(word_all) - i - 1)
        word = word_all[w_index]
        random_word.append(word)
        word_all.remove(word)
        print(len(word_all))
    random.shuffle(random_word)
    return random_word


# pprint(get_words(get_all_word('cw_english_words')))


def make_quiz(meanings, word):
    meaning = word.meaning
    ms = meanings.copy()
    ms.remove(meaning)
    # print(">>> ms:", ms)
    answers = random.sample(ms, 3)
    # print(">>> answers:", answers)
    answers.append(meaning)
    random.shuffle(answers)
    return answers
