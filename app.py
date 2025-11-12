# app.py — Search Intent Analyzer (Firecrawl + Classifier), Intent Fixes
# Version: 1.4.0
# Author: Knovik • Madusanka Premaratne (Madus)

import os, re, json, math, datetime as dt
from typing import List, Dict, Any, Tuple
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px

try:
    from search_intent_classifier import SearchIntentClassifier, Intent  # type: ignore
except Exception:
    SearchIntentClassifier, Intent = None, None

__version__ = "1.4.0"
AUTHOR = "Knovik Engineering Team"
FIRECRAWL_KEY = os.getenv("FIRECRAWL_API_KEY", "")

FIRECRAWL_SEARCH_URL = "https://api.firecrawl.dev/v2/search"

INTENT_COLORS = {"Informational":"#2563eb","Transactional":"#16a34a","Navigational":"#f59e0b","Commercial Investigation":"#ef4444"}
CARD_CSS = '<style>.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600;color:white}.card{border:1px solid #e6e6e6;border-radius:14px;padding:14px 16px;margin-bottom:12px;background:#fff}.card h4{margin:0 0 6px 0}.kv{font-size:13px;color:#444}.kv b{color:#111}.smallmuted{color:#666;font-size:12px}</style>'

st.set_page_config(page_title="Search Intent Analyzer", page_icon="🔎", layout="wide")
st.markdown(CARD_CSS, unsafe_allow_html=True)
def badge(text, color): return f'<span class="badge" style="background:{color}">{text}</span>'

def hero_banner():
    st.markdown(f'<div style="text-align:center;padding:18px 8px;border-top:1px solid #e6e6e6;"><h2 style="margin:6px 0 10px 0;">Search Intent Analyzer v{__version__}</h2><p style="margin:6px 0 6px 0;">Built by <strong>{AUTHOR}</strong></p><p style="margin:0;">Powered by Firecrawl + Hybrid Classifier</p></div>', unsafe_allow_html=True)

def app_footer():
    st.markdown(f'<hr style="margin-top:36px;"/><div style="text-align:center;font-size:13px;color:#666;padding-bottom:12px;"><div><strong>Search Intent Analyzer</strong> • v{__version__}</div><div>© {dt.datetime.now().year} {AUTHOR} — MIT License</div></div>', unsafe_allow_html=True)

hero_banner()

with st.sidebar:
    st.header('Settings'); st.caption(f'Version: {__version__} • Author: {AUTHOR}')
    st.subheader('Scoring Weights (%)')
    w_serp   = st.slider('SERP-like signals', 0, 100, 25)
    w_rules  = st.slider('Keyword modifiers (rules)', 0, 100, 20)
    w_pages  = st.slider('Top pages content cues', 0, 100, 25)
    clf_weight = st.slider('Classifier weight (hybrid)', 0, 100, 30)
    st.divider(); st.subheader('Firecrawl (required)')
    fc_key_ui = st.text_input('FIRECRAWL_API_KEY', FIRECRAWL_KEY, type='password')
    if fc_key_ui: FIRECRAWL_KEY = fc_key_ui
    country = st.text_input('Country code (ISO)', 'US')
    location = st.text_input('Location (optional)', '')
    limit = st.slider('Number of results', 1, 20, 10)
    st.divider(); st.subheader('Rules')
    informational_mods = st.text_area('Informational', 'how,what,why,who,guide,tutorial,learn,meaning,definition,ideas,examples,steps')
    transactional_mods = st.text_area('Transactional', 'buy,price,deal,discount,coupon,book,order,subscribe,download')
    navigational_mods = st.text_area('Navigational', 'brand,login,official,homepage,near me,locations,contact')
    commercial_mods = st.text_area('Commercial Investigation', 'best,top,vs,review,compare,comparison,alternative,pros,cons')

INTENTS = ['Informational','Transactional','Navigational','Commercial Investigation']
INTEGRATION_VERBS = ["connect","pair","link","use","enable","setup","set up","add","integrate","bridge","work with","works with"]
BRAND_LEXICON = ["alexa","amazon","apple","homekit","siri","homepod","google","nest","assistant","smartthings","ikea","philips hue"]

def contains_any(s, words):
    s_low = s.lower(); return any(w.strip().lower() in s_low for w in words if w.strip())

def detect_brand_pairs(texts):
    seen=set()
    for t in texts:
        tl=t.lower()
        for b in BRAND_LEXICON:
            if b in tl: seen.add(b)
    return len(seen)

def firecrawl_search(query, limit=10, country='US', location=''):
    if not FIRECRAWL_KEY: raise RuntimeError('FIRECRAWL_API_KEY not set')
    headers={'Authorization': f'Bearer {FIRECRAWL_KEY}', 'Content-Type':'application/json'}
    payload={'query':query,'limit':limit,'country':country,'location':location or None,'sources':['web'],'scrapeOptions':{'formats':['markdown','html'],'onlyMainContent':True,'storeInCache':True}}
    payload={k:v for k,v in payload.items() if v not in (None,'',[])}
    r=requests.post('https://api.firecrawl.dev/v2/search', headers=headers, json=payload, timeout=60); r.raise_for_status(); return r.json()

def map_features_to_intents_from_fc(items, query):
    score={i:0.0 for i in INTENTS}
    texts=[query]+[" ".join([str(it.get('title','')),str(it.get('description','')),str(it.get('markdown',''))]) for it in items[:10]]
    joined=" 
 ".join(texts).lower()
    if any(k in joined for k in ['faq','people also ask','how to','guide','tutorial']): score['Informational']+=0.6
    if any(k in joined for k in ['buy','price','add to cart','checkout','shop']): score['Transactional']+=0.6
    if any(k in joined for k in ['official site','login','contact us']): score['Navigational']+=0.4
    if any(k in joined for k in ['review','best','top',' vs ','comparison']): score['Commercial Investigation']+=0.6
    if any(v in joined for v in INTEGRATION_VERBS): score['Informational']+=0.8
    if detect_brand_pairs(texts)>=2: score['Informational']+=0.6
    return score

def map_modifiers_to_intents(q, mods):
    score={i:0.0 for i in INTENTS}
    if contains_any(q,mods['informational']): score['Informational']+=1
    if contains_any(q,mods['transactional']): score['Transactional']+=1
    if contains_any(q,mods['navigational']): score['Navigational']+=1
    if contains_any(q,mods['commercial']): score['Commercial Investigation']+=1
    if contains_any(q, INTEGRATION_VERBS): score['Informational']+=0.8
    if detect_brand_pairs([q])>=2: score['Informational']+=0.6
    return score

def analyze_top_pages(items, max_pages):
    score={i:0.0 for i in INTENTS}; notes=[]
    for it in items[:max_pages]:
        url=it.get('url'); markdown=(it.get('markdown') or '').lower(); html=(it.get('html') or '').lower()
        ctas=[t for t in ['buy now','add to cart','order','checkout','subscribe','sign up','download','contact'] if t in markdown or t in html]
        schema=[]
        if 'faq' in markdown or 'faqpage' in html: schema.append('FAQ')
        if 'howto' in html or 'how-to' in html: schema.append('HowTo')
        if 'product' in html and ('price' in html or 'sku' in html): schema.append('Product')
        if 'review' in markdown or 'aggregaterating' in html: schema.append('Review')
        if ctas or 'Product' in schema: score['Transactional']+=1
        if 'FAQ' in schema or 'HowTo' in schema: score['Informational']+=1
        if 'Review' in schema: score['Commercial Investigation']+=1
        if 'Product' in schema and ('FAQ' in schema or 'HowTo' in schema):
            score['Informational']+=0.7; score['Transactional']=max(0.0, score['Transactional']-0.3)
        if any(v in markdown for v in INTEGRATION_VERBS): score['Informational']+=0.5
        notes.append({'url':url,'ctas':ctas,'schema':schema})
    return score, notes

def map_classifier_scores(clf_scores):
    out={i:0.0 for i in INTENTS}
    for k,v in clf_scores.items():
        key=k.value if hasattr(k,'value') else str(k); key=key.lower()
        if 'transactional' in key: out['Transactional']+=v/100.0
        elif 'navigational' in key: out['Navigational']+=v/100.0
        elif 'commercial' in key: out['Commercial Investigation']+=v/100.0
        elif 'problem' in key or 'information' in key: out['Informational']+=v/100.0
    s=sum(out.values()) or 1.0; return {k:vv/s for k,vv in out.items()}

def combine_scores(s_serp,s_rules,s_pages,w_serp,w_rules,w_pages,s_clf=None,clf_weight=0):
    combined={i:0.0 for i in INTENTS}
    for i in INTENTS:
        base=(w_serp/100)*s_serp.get(i,0.0)+(w_rules/100)*s_rules.get(i,0.0)+(w_pages/100)*s_pages.get(i,0.0)
        if s_clf: base=(1-clf_weight/100.0)*base+(clf_weight/100.0)*s_clf.get(i,0.0)
        combined[i]=base
    return combined

def label_from_scores(scores):
    eps=1e-6; total=sum(scores.values())+eps; probs={k:(v/total) for k,v in scores.items()}
    primary=max(probs, key=probs.get)
    secondary=sorted([k for k in probs if k!=primary], key=lambda x: probs[x], reverse=True)[0]
    top1=probs[primary]; top2=probs[secondary]; margin=(top1-top2)/(top1+top2+eps)
    ent=-sum(p*math.log(p+eps) for p in probs.values())/math.log(len(probs))
    confidence=max(0.0,(1-ent))*margin*100.0; branching='Mixed Intent' if ent>0.85 else 'Clear'
    return primary, secondary, round(confidence,1), branching

tab_input, tab_results, tab_overview = st.tabs(['➊ Input','➋ Results','➌ Overview'])
with tab_input:
    st.subheader('Enter keywords')
    kws_text=st.text_area('One keyword per line', height=160, placeholder='e.g. alexa homekit')
    run_btn=st.button('Run Analysis', type='primary')

def run_for_keyword(q):
    data=firecrawl_search(q, limit=limit, country=country, location=location)
    items=(data.get('data') or {}).get('web', [])
    s_serp=map_features_to_intents_from_fc(items, q)
    mods={'informational':[m.strip() for m in informational_mods.split(',') if m.strip()],
          'transactional':[m.strip() for m in transactional_mods.split(',') if m.strip()],
          'navigational':[m.strip() for m in navigational_mods.split(',') if m.strip()],
          'commercial':[m.strip() for m in commercial_mods.split(',') if m.strip()]}
    s_rules=map_modifiers_to_intents(q, mods)
    s_pages, page_notes=analyze_top_pages(items, max_pages=5)
    s_clf=None; clf_scores_json="{}"
    if SearchIntentClassifier is not None:
        try:
            clf=SearchIntentClassifier()
            urls=[it.get('url') for it in items if it.get('url')]; titles=[it.get('title') or '' for it in items]
            primary_enum, clf_scores=clf.classify_intent(urls, titles)
            s_clf=map_classifier_scores(clf_scores)
            clf_scores_json=json.dumps({(k.value if hasattr(k,'value') else str(k)): v for k,v in clf_scores.items()})
        except Exception: s_clf=None
    combined=combine_scores(s_serp, s_rules, s_pages, w_serp, w_rules, w_pages, s_clf=s_clf, clf_weight=clf_weight)
    primary, secondary, confidence, branch=label_from_scores(combined)
    top_urls=[it.get('url') for it in items[:10] if it.get('url')]
    return {'keyword':q,'primary_intent':primary,'secondary_intent':secondary,'confidence_pct':confidence,'branching':branch,
            'top_urls':json.dumps(top_urls),'scores':json.dumps(combined),'notes':json.dumps(page_notes),'clf_scores':clf_scores_json}

if run_btn:
    kw_list=[k.strip() for k in (kws_text or '').splitlines() if k.strip()]; kw_list=list(dict.fromkeys(kw_list))
    if not FIRECRAWL_KEY: st.error('Please provide FIRECRAWL_API_KEY in the sidebar or environment.')
    elif not kw_list: st.warning('Please enter at least one keyword.')
    else:
        rows=[]; progress=st.progress(0)
        for i,q in enumerate(kw_list, start=1):
            try: rows.append(run_for_keyword(q))
            except Exception as e: rows.append({'keyword':q,'primary_intent':'','secondary_intent':'','confidence_pct':0,'branching':'Error','top_urls':'[]','scores':'{}','notes':json.dumps({'error':str(e)}),'clf_scores':'{}'})
            progress.progress(int(i/len(kw_list)*100))
        progress.empty(); st.session_state['result_df']=pd.DataFrame(rows); st.success('Done! See the Results tab.')

with tab_results:
    df=st.session_state.get('result_df')
    if df is None or df.empty: st.info('Run an analysis to see results.')
    else:
        st.subheader('Filters')
        intents_sel=st.multiselect('Primary intent', INTENTS, default=INTENTS)
        min_conf=st.slider('Min confidence (%)', 0, 100, 0)
        query=st.text_input('Search keyword', '')
        mask=df['primary_intent'].isin(intents_sel) & (df['confidence_pct']>=min_conf)
        if query.strip(): mask&=df['keyword'].str.contains(re.escape(query), case=False, na=False)
        fdf=df[mask].copy()
        c1,c2,c3,c4=st.columns(4)
        with c1: st.metric('Keywords', len(fdf))
        with c2: st.metric('Avg confidence', f"{fdf['confidence_pct'].mean():.1f}%" if len(fdf) else '—')
        with c3: st.metric('Mixed intents', int((fdf['branching']=='Mixed Intent').sum()) if len(fdf) else 0)
        with c4: st.metric('Clear intents', int((fdf['branching']=='Clear').sum()) if len(fdf) else 0)
        st.divider(); st.subheader('Keyword Cards')
        for _,r in fdf.sort_values(by=['confidence_pct','primary_intent'], ascending=[False, True]).iterrows():
            color=INTENT_COLORS.get(r['primary_intent'], '#374151'); urls=json.loads(r['top_urls'] or '[]'); badge_html=badge(r['primary_intent'], color)
            st.markdown(f'<div class="card"><h4>{r["keyword"]} {badge_html}</h4><div class="kv"><b>Secondary:</b> {r["secondary_intent"]} • <b>Confidence:</b> {r["confidence_pct"]:.1f}% • <b>Status:</b> {r["branching"]}</div><div class="smallmuted">{", ".join(urls[:3]) if urls else "No URLs captured"}</div></div>', unsafe_allow_html=True)
            with st.expander('Details & Notes'):
                st.json(json.loads(r['notes'] or '{}'))
                try:
                    st.markdown('**Classifier scores (raw):**'); st.json(json.loads(r.get('clf_scores','{}')))
                except Exception: pass
        st.divider(); st.subheader('Table')
        st.dataframe(fdf, use_container_width=True, column_config={'confidence_pct': st.column_config.ProgressColumn('Confidence %', max_value=100, format='%.1f%%'),'top_urls': st.column_config.TextColumn('Top URLs (JSON)')})
        st.download_button('Download filtered CSV', fdf.to_csv(index=False).encode('utf-8'), 'intent_report_filtered.csv', 'text/csv')

with tab_overview:
    df=st.session_state.get('result_df')
    if df is None or df.empty: st.info('Run an analysis to see results.')
    else:
        st.subheader('Intent Distribution')
        counts=df['primary_intent'].value_counts().reset_index(); counts.columns=['intent','count']
        fig=px.pie(counts, names='intent', values='count', hole=0.45); st.plotly_chart(fig, use_container_width=True)
        st.subheader('Confidence by Intent')
        fig2=px.box(df, x='primary_intent', y='confidence_pct', color='primary_intent', color_discrete_map=INTENT_COLORS); st.plotly_chart(fig2, use_container_width=True)

app_footer()
