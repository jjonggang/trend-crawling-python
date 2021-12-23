import csv
from datetime import datetime
from lexrankr import LexRank
import requests as rq
from bs4 import BeautifulSoup
from typing import List
from konlpy.tag import Okt, Twitter
# from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt

import tweepy

# StreamListener error발생시
# pip install tweepy==3.10.0


class OktTokenizer:
    okt: Okt = Okt()

    def __call__(self, text: str) -> List[str]:
        tokens: List[str] = self.okt.pos(text, norm=True, stem=True, join=True)
        return tokens


def start(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
    data = rq.get(url, headers=headers).content
    return BeautifulSoup(data, "html.parser")


def zum_crawler():
    url = 'https://issue.zum.com/daily'
    soup = start(url)
    trend_result = []
    keyword_group = soup.find('ul', {'id': 'issueKeywordList'}).find_all('li')
    for keyword_list in keyword_group:
        keywords = keyword_list.find_all('span', {'class': 'word'})
        for k in keywords:
            trend_result.append(k.string)
    return trend_result


def print_result(trend_result, country):
    if country == "kr":
        print("*국내 트렌드")
    else:
        print("*해외 트렌드")
    now = datetime.now().strftime('%Y.%m.%d %H:%M')
    print("현재 시간: " + now)
    for i in range(0, 10):
        print(f"{i + 1}위. " + trend_result[i])


def news_main_crawling(url):
    soup = start(url)
    news = soup.find('div', {'id': 'harmonyContainer'}).find('section')
    paragraph_list = news.find_all('p')
    paragraph = []
    for p in paragraph_list:
        if p.string == None:
            continue
        paragraph.append(p.string)
    paragraph_string = ''.join(paragraph)
    return paragraph_string


def trend_summarize(paragraph):
    print("\n트렌드를 요약중입니다.. 잠시만 기다려주세요\n")
    mytokenizer: OktTokenizer = OktTokenizer()
    lexrank: LexRank = LexRank(mytokenizer)
    lexrank.summarize(paragraph)
    summaries: List[str] = lexrank.probe()
    # print(summaries)
    print("트렌드 요약문: ")
    for i in summaries:
        print("- ", i)


# def trend_word_cloud(paragraph_string):
#     twitter = Twitter()
#
#     # twitter함수를 통해 읽어들인 내용의 형태소를 분석한다.
#     sentences_tag = []
#     sentences_tag = twitter.pos(paragraph_string)
#
#     noun_adj_list = []
#
#     for word, tag in sentences_tag:
#         if tag in ['Noun', 'Adjective']:
#             noun_adj_list.append(word)
#     counts = Counter(noun_adj_list)
#     tags = counts.most_common(20)
#
#     wc = WordCloud(font_path=['./BinggraeSamanco.otf'], background_color="white", max_font_size=60)
#     cloud = wc.generate_from_frequencies(dict(tags))
#
#     plt.figure(figsize=(10, 8))
#     plt.axis('off')
#     plt.imshow(cloud)
#     plt.show()

def trend_search(trend_list):
    print_result(trend_list, 'kr')
    i = int(input("\n검색을 원하는 항목을 선택하세요!")) - 1
    url = f'https://m.search.daum.net/search?w=news&nil_search=btn&DA=NTB&enc=utf8&cluster=y&cluster_page=1&q={trend_list[i]}'
    soup = start(url)
    news_num = 1
    while True:
        news_content = soup.find('li', {"id": f"news_{news_num}"})
        news_url = news_content.a['href']
        if news_url[8:10] == 'cp':
            news_num = news_num + 1
            continue
        else:
            break
    print(news_url)
    # news_office = news_content.span.span.string
    soup = start(news_url)
    news = soup.find('div', {"id": "kakaoContent"})

    news_title = news.h3.text
    news_office = news.img['alt']
    news_img = news.find('p', {'class': 'link_figure'})
    if news_img is not None:
        news_img = news_img.img['src']
    else:
        print('no image')
    # news_main = news.
    print(f"뉴스 제목: {news_title}")
    print(f"신문사: {news_office}")
    print(f"이미지: {news_img}")
    paragraph_string = news_main_crawling(news_url)
    # trend_summaries = trend_summarize(paragraph_string)
    # f = open(f'{trend_list[i]}.csv', 'w', encoding='utf-8', newline='')  # 파일오픈
    # csvWriter = csv.writer(f)
    # csvWriter.writerow(trend_summaries)
    # f.close()

    # 트렌드 요약문 출력하기
    trend_summarize(paragraph_string)

    #
    # while True:
    #     trend_showing_input = int(input("원하는 작업을 선택하세요!(1. 트렌드 요약문 보기, 2. 트렌드 워드클라우드 보기, 3. 나가기)"))
    #     ## 트렌드 요약문 출력하기
    #     if trend_showing_input == 1:
    #         trend_summarize(paragraph_string)
    #         # print("트렌드 요약문: ")
    #         # for i in trend_summaries:
    #         #     print("- ", i)
    #     elif trend_showing_input == 2:
    #         # trend_word_cloud(paragraph_string)


trend_list = zum_crawler()
while True:
    trend_search(trend_list)
    print("\n원하는 작업을 선택하세요!")
    user_input = int(input("1. 추가 검색, 2. 프로그램 종료"))
    if user_input == 1:
        print("트렌드를 다시 검색합니다..")
        continue
    elif user_input == 2:
        print("프로그램을 종료합니다..")
        break
    else:
        print("잘못된 입력입니다. 프로그램을 종료합니다.")
        break


