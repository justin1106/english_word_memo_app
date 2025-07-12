import streamlit as st
import extra_streamlit_components as stx
import time
from func import *
from pocketbase import PocketBase
import random as r
import config

client = PocketBase(config.POCKETBASE_URL)
whole_page = 100

if "page" not in st.session_state:
    st.session_state["page"] = 1

if "all_words" not in st.session_state:
    st.session_state["all_words"] = []
    for p in range(whole_page):
        for w in get_all_word("cw_english_words", p + 1):
            st.session_state["all_words"].append(w)

if "words" not in st.session_state:
    st.session_state["words"] = get_words(st.session_state["all_words"])

if "meanings" not in st.session_state:
    st.session_state["meanings"] = []

if "test_result" not in st.session_state:
    st.session_state["test_result"] = []

if "user" not in st.session_state:
    st.session_state["user"] = "choun"


def make_results():
    st.session_state["results"] = []
    results = client.collection("cw_english_words_results").get_list()
    for re in results.items:
        st.session_state["results"].append({"en_word_id": re.en_word_id, "id": re.id})


if "results" not in st.session_state:
    make_results()


def make_meanings():
    st.session_state["meanings"] = []
    for w in st.session_state["all_words"]:
        st.session_state["meanings"].append(w.meaning)


def make_questions():
    st.session_state["questions"] = []
    for word in st.session_state["words"]:
        make_meanings()
        question = {}
        question["id"] = word.id
        question["word"] = word.word
        question["meaning"] = word.meaning
        question["quiz"] = make_quiz(st.session_state["meanings"], word)
        question["example"] = word.example1
        question["user_answer"] = ""
        question["iscorrect"] = None
        st.session_state["questions"].append(question)

        # print("meanings: ", st.session_state["meanings"])

    # print(">>> questions:", st.session_state["questions"])


if "questions" not in st.session_state:
    make_questions()


def init_router():
    return stx.Router({"/": home, "/home": home, "/result": finish_test})


def is_in_db(en_word_id):
    isTrue = None
    for re in st.session_state["results"]:
        if re["en_word_id"] == en_word_id:
            isTrue = True
            return True, re["id"]
    if not isTrue:
        return False, None


def show_word(word):
    en_word = word["word"]
    meaning = word["meaning"]
    example = word["example"]
    w_id = word["id"]
    choices = word["quiz"]
    st.title(en_word)
    st.subheader(f"ex) {example}")
    b1 = st.button(choices[0], use_container_width=True)
    if b1:
        if choices[0] == meaning:
            word["iscorrect"] = True
            word["user_answer"] = choices[0]
            next_page()
        else:
            word["iscorrect"] = False
            word["user_answer"] = choices[0]
            next_page()

    b2 = st.button(choices[1], "2", use_container_width=True)
    if b2:
        if choices[1] == meaning:
            word["iscorrect"] = True
            word["user_answer"] = choices[1]
            next_page()
        else:
            word["iscorrect"] = False
            word["user_answer"] = choices[1]
            next_page()

    b3 = st.button(choices[2], "3", use_container_width=True)
    if b3:
        if choices[2] == meaning:
            word["iscorrect"] = True
            word["user_answer"] = choices[2]
            next_page()
        else:
            word["iscorrect"] = False
            word["user_answer"] = choices[2]
            next_page()

    b4 = st.button(choices[3], "4", use_container_width=True)
    if b4:
        if choices[3] == meaning:
            word["iscorrect"] = True
            word["user_answer"] = choices[3]
            next_page()
        else:
            word["iscorrect"] = False
            word["user_answer"] = choices[3]
            next_page()


def home():
    date = time.strftime("%Y/%m/%d", time.localtime(time.time()))
    st.subheader(date)
    st.write("<hr>", unsafe_allow_html=True)
    word = st.session_state["questions"][st.session_state["page"] - 1]
    show_word(word)
    st.write("<hr>", unsafe_allow_html=True)
    st.subheader(f"{st.session_state['page']}/10")


def finish_test():
    cor_num = 0
    for l in st.session_state["questions"]:
        if l["iscorrect"] == True:
            cor_num += 1

    st.title("결과")
    info_text = ""

    for idx, l in enumerate(st.session_state["questions"]):
        if l["iscorrect"]:
            info_text += f"{idx+1}. O  단어: {l['word']} |   입력한 답: {l['user_answer']} | 정답: {l['meaning']}\n"
        else:
            info_text += f"{idx+1}. X  단어: {l['word']} | 입력한 답: {l['user_answer']} | 정답: {l['meaning']}\n"
    st.subheader(f"총점: {cor_num*100//10}/100")
    more_info = st.expander("자세히 보기")
    more_info.write(info_text)

    result_to_db(st.session_state["questions"])


def next_page():
    if st.session_state["page"] < 10:
        st.session_state["page"] += 1
        st.rerun()
    else:
        router.route("/result")


def result_to_db(result):
    st.session_state["words"] = get_words(st.session_state["all_words"])
    make_questions()
    for r in result:
        in_db, id = is_in_db(r["id"])
        # print(in_db)
        if in_db:
            if r["iscorrect"]:
                client.collection("cw_english_words_results").update(
                    id, {"iscorrect": True}
                )
        else:
            client.collection("cw_english_words_results").create(
                {
                    "en_word_id": r["id"],
                    "user_id": st.session_state["user"],
                    "iscorrect": r["iscorrect"],
                }
            )


router = init_router()
router.show_route_view()
