#!/usr/bin/env python3
import argparse, json, time, warnings
import wikipedia
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore', category=UserWarning)
def safe_search(title):
    try:
        res = wikipedia.search(title, results=3)
        if not res: return None
        if title in res: return title
        return res[0]
    except: return None
def fetch_summary(title):
    try:
        page = wikipedia.page(title, auto_suggest=False)
        return page.summary, page.url, page.html()
    except:
        s = safe_search(title); 
        if not s: return None, None, None
        try:
            page = wikipedia.page(s, auto_suggest=False); return page.summary, page.url, page.html()
        except: return None, None, None
def main(inp, outp):
    with open(inp,'r',encoding='utf-8') as f: items=[l.strip() for l in f if l.strip()]
    db=[]
    for name in items:
        summary, url, html = fetch_summary(name)
        entry={'name':name,'summary':summary or '','source':url or '','facts':[]}
        if summary:
            sents=[s.strip() for s in summary.replace('\n',' ').split('. ') if s.strip()]
            entry['facts']=sents[:10]
        else:
            if html:
                soup=BeautifulSoup(html, features='html.parser')
                paras=soup.find_all('p')
                for p in paras:
                    txt=p.get_text().strip()
                    if len(txt)>120:
                        sents=[s.strip() for s in txt.split('. ') if s.strip()]
                        entry['facts']=sents[:10]; break
        db.append(entry); time.sleep(0.25)
    with open(outp,'w',encoding='utf-8') as f: json.dump(db,f,ensure_ascii=False, indent=2)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--input'); p.add_argument('--output'); a=p.parse_args(); main(a.input,a.output)
