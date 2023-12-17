from goose3 import Goose
from goose3.text import StopWordsChinese
from bs4 import BeautifulSoup
import requests
import os


g = Goose({'stopwords_class': StopWordsChinese, 'parser_class': 'soup'})

# 获取缠论的所有文章链接
base_url = 'http://www.fxgan.com/chan_fenlei/'

content = g.extract(url=base_url + "index.htm#@")


def get_urls(elements):
    return [base_url + e.xpath('./a/@href')[0] for e in elements]


def get_article(url):
    try:
        article = g.extract(url=url)
        title = article.title
        soup = BeautifulSoup(article.raw_html)
    except:
        r = requests.get(url)
        r.encoding = 'gb2312'
        soup = BeautifulSoup(r.text)
        title = soup.title.string if soup.title else None
    if title is None:
        return None, None
    print("parse article: " + title)

    main = soup.find(id="sina_keywｏｒd_ad_area2")
    if main is None:
        return None, None
    divs = main.find_all('div')
    full_text = ""
    for div in divs:
        paragraphs = div.find_all('p')
        if len(paragraphs) > 0:
            for p in paragraphs:
                if len(p.text.strip()) > 0:
                    # if p and len(p.text.strip()) == p.text.count('\xa0'): continue
                    full_text += p.text + "<br>\n"
        if div.font is None:
            continue
        if len(div.text.strip()) <= 1:
            continue
        if "更多文章请点击进入缠中说禅" in div.text:
            continue
        full_text += div.text + "</br>\n"
    return title, full_text


def get_lunyu(cate, folder):
    xpath = '//*[@id="%s"]/li' % cate
    chanlun_url_list = content.doc.xpath(xpath)
    urls = get_urls(chanlun_url_list)
    print(len(urls))
    for url in urls:
        title, text = get_article(url)
        if title is None or text is None:
            print('fail to parse ' + url)
        with open("./%s/" % folder + title.replace('/', '') + ".md", "w") as f:
            f.write(text)


category_map = {'说缠': 'ulTexts_Cate4',
                '时政': 'ulTexts_Cate2',
                '缠论': 'ulTexts_Cate11',
                '论语': 'ulTexts_Cate7'
                }
for k, v in category_map.items():
    if not os.path.exists(k):
        os.makedirs(k)
    get_lunyu(v, k)
print('task done')
