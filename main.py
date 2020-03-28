import codecs
import os
import urllib.request
from pathlib import Path
from time import strptime, strftime
from xml.etree import ElementTree

from html2text import html2text

url = 'https://trends.google.com/trends/trendingsearches/daily/rss?geo=FR'
keywords_filename = Path('.').resolve() / 'keywords_tmp.txt'
tmp_filename = Path('.').resolve() / 'keywords_tmp.xml'

urllib.request.urlretrieve(url, tmp_filename)

if os.path.isfile(keywords_filename):
    with open(keywords_filename, 'r') as f:
        old_list = f.read().splitlines()
else:
    old_list = []

tree = ElementTree.parse(tmp_filename)
root = tree.getroot()

fresh_list = [title.text.lower()
              for title in root.iter('title')]
try:
    fresh_list.remove('daily search trends')
except ValueError:
    pass

output = '\n'.join(a for a in list(set(old_list + fresh_list)))

with codecs.open(keywords_filename, 'w+', "utf-8") as f:
    f.write(output)


try:
    os.remove(tmp_filename)
except FileNotFoundError:
    pass
try:
    os.remove(keywords_filename)
except FileNotFoundError:
    pass

# <ht:picture></ht:picture> means: "picture" belongs to the namespace "ht"
# -> At the declaration, the namespace "ht" is this:
# xmlns:ht='https://trends.google.com/trends/trendingsearches/daily'
# -> so you *MUST* precise the namespace.
# item.find('ht:picture')            -> wont work!
# item.find('ht:picture', NAMESPACE) -> will work !
def to_text(txt):
    return html2text(txt).replace('\n', ' ').replace('\r', '').strip()


HT_NS = {'ht': 'https://trends.google.com/trends/trendingsearches/daily'}
for item in root.iter('item'):
    print('-' * 90)
    print(item.find('pubDate').text.strip())
    pub_date = strptime(item.find('pubDate').text.strip(),
                        '%a, %d %b %Y %H:%M:%S %z')
    print(strftime('%d/%m/%Y, %H:%M:%S', pub_date))
    # print(item.find('ht:picture', HT_NS).text)
    for news_i in item.findall('ht:news_item', HT_NS):
        src = to_text(news_i.find('ht:news_item_source', HT_NS).text)
        if src.lower() in ['public.fr', 'voici']:
            continue
        print('  >', f'{src} :')
        print('   ', to_text(news_i.find('ht:news_item_title', HT_NS).text))
        print('   ', to_text(news_i.find('ht:news_item_snippet', HT_NS).text))
        print('   ', news_i.find('ht:news_item_url', HT_NS).text)

