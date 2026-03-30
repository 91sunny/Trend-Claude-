"""
===============================================================
  🧒 아동복 트렌드 대시보드 v3  —  app.py
  실행: streamlit run app.py
===============================================================
"""

import os, streamlit as st, pandas as pd, plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="아동복 트렌드 대시보드", page_icon="👗",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
html,body,[class*="css"]{font-family:'Apple SD Gothic Neo','Pretendard',sans-serif}
.dash-title{font-size:1.6rem;font-weight:700;color:#111;margin:0}
.dash-sub  {font-size:.82rem;color:#aaa;margin:.1rem 0 1rem}
.platform-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-bottom:16px}
.ptile{border-radius:12px;padding:10px 12px;display:flex;align-items:center;gap:9px;
       text-decoration:none;border:0.5px solid rgba(0,0,0,.08);transition:opacity .15s}
.ptile:hover{opacity:.82}
.ptile-icon{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;
            justify-content:center;font-size:15px;flex-shrink:0;color:#fff}
.ptile-name{font-size:.8rem;font-weight:600;color:#111}
.ptile-sub {font-size:.68rem;color:#888;margin-top:1px}
.kpi-wrap{background:#fff;border:1px solid #eee;border-radius:12px;padding:.85rem 1rem;text-align:center}
.kpi-l{font-size:.68rem;color:#bbb;text-transform:uppercase;letter-spacing:.05em}
.kpi-v{font-size:1.5rem;font-weight:700;color:#111;line-height:1.2}
.kpi-s{font-size:.68rem;color:#ccc;margin-top:.1rem}
.b-hot   {background:#ff3b57;color:#fff;font-size:9px;font-weight:800;padding:1px 5px;border-radius:3px}
.b-trend {background:#e87700;color:#fff;font-size:9px;font-weight:800;padding:1px 5px;border-radius:3px}
.b-new   {background:#3346cc;color:#fff;font-size:9px;font-weight:800;padding:1px 5px;border-radius:3px}
.pcard{background:#fff;border:1px solid #eee;border-radius:14px;overflow:hidden;transition:box-shadow .2s,transform .2s}
.pcard:hover{box-shadow:0 6px 20px rgba(0,0,0,.07);transform:translateY(-2px)}
.pimg-wrap{width:100%;aspect-ratio:1/1;overflow:hidden;background:#f5f5f5;
           display:flex;align-items:center;justify-content:center;position:relative}
.pimg-wrap img{width:100%;height:100%;object-fit:cover}
.pbadges{position:absolute;top:6px;left:6px;display:flex;flex-wrap:wrap;gap:2px}
.psrc-pill{position:absolute;bottom:6px;right:6px;padding:2px 7px;border-radius:20px;
           font-size:9px;font-weight:700;color:#fff}
.pinfo{padding:.65rem .8rem .8rem}
.ptag{display:inline-block;font-size:9px;font-weight:600;padding:1px 5px;border-radius:20px;margin-bottom:3px}
.pname{font-size:.8rem;font-weight:600;color:#111;line-height:1.35;margin-bottom:2px;
       display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pbrand{font-size:.72rem;color:#aaa;margin-bottom:2px}
.pprice{font-size:1rem;font-weight:700;color:#e8384f}
.pmall {font-size:.68rem;color:#ccc;margin-top:1px}
.noimg{width:100%;aspect-ratio:1/1;background:#f0f0f0;display:flex;align-items:center;justify-content:center;font-size:2rem;color:#ccc}
.sec-head{font-size:.95rem;font-weight:700;color:#111;margin:1.2rem 0 .6rem;display:flex;align-items:center;gap:.3rem}
hr.div{border:none;border-top:1px solid #f0f0f0;margin:1rem 0}
[data-testid="stSidebar"]{background:#fafafa;border-right:1px solid #f0f0f0}
.sb-lbl{font-size:.67rem;font-weight:700;color:#bbb;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.35rem}
</style>
""", unsafe_allow_html=True)

PLATFORMS = [
    {"name":"쿠팡 키즈",   "sub":"로켓배송 아동복",   "url":"https://www.coupang.com/np/search?q=%ED%82%A4%EC%A6%88+%EC%95%84%EB%8F%99%EB%B3%B5",  "color":"C0392B","icon":"🛒"},
    {"name":"네이버 쇼핑", "sub":"국내 최대 쇼핑몰",   "url":"https://search.shopping.naver.com/search/all?query=%EC%95%84%EB%8F%99%EB%B3%B5",        "color":"03C75A","icon":"🔍"},
    {"name":"무신사 키즈", "sub":"키즈 컬렉션",        "url":"https://www.musinsa.com/main/kids/recommend?gf=F",                                       "color":"1A1A1A","icon":"👟"},
    {"name":"Instagram",   "sub":"#키즈패션",          "url":"https://www.instagram.com/explore/tags/%ED%82%A4%EC%A6%88%ED%8C%A8%EC%85%98/",           "color":"E1306C","icon":"📸"},
    {"name":"Pinterest",   "sub":"키즈 트렌드 핀",     "url":"https://kr.pinterest.com/search/pins/?q=%ED%82%A4%EC%A6%88%ED%8C%A8%EC%85%98",           "color":"E60023","icon":"📌"},
    {"name":"Amazon",      "sub":"Kids Fashion",       "url":"https://www.amazon.com/s?k=kids+fashion&i=fashion-womens-intl-ship",                      "color":"FF9900","icon":"📦"},
    {"name":"H&M Kids",    "sub":"글로벌 키즈 브랜드", "url":"https://www2.hm.com/ko_kr/kids.html",                                                    "color":"E50010","icon":"🇸🇪"},
    {"name":"ZARA Kids",   "sub":"신상품 바로가기",    "url":"https://www.zara.com/kr/ko/kids-l1037.html",                                              "color":"111111","icon":"✦"},
]

@st.cache_data
def load_data():
    for fname in ["all_data.csv","kids_data.csv"]:
        if not os.path.exists(fname): continue
        df = pd.read_csv(fname, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
        df["최저가"]     = pd.to_numeric(df.get("최저가",0), errors="coerce").fillna(0).astype(int)
        df["브랜드"]     = df.get("브랜드","").fillna("").replace("","브랜드 없음")
        df["판매처"]     = df.get("판매처","").fillna("판매처 미상").replace("","판매처 미상")
        df["이미지URL"]  = df.get("이미지URL","").fillna("")
        df["판매처링크"] = df.get("판매처링크","").fillna("")
        df["출처"]       = df.get("출처","국내").fillna("국내")
        df["플랫폼"]     = df.get("플랫폼","기타").fillna("기타")
        df["플랫폼색상"] = df.get("플랫폼색상","888888").fillna("888888")
        df["is_new"]     = df.get("is_new",False).fillna(False).astype(bool)
        df["is_hot"] = False; df["is_trending"] = False
        for kw in df["검색키워드"].unique():
            m = df["검색키워드"]==kw; sub = df.loc[m,"최저가"]
            if len(sub)>=5:
                df.loc[m & df["최저가"].between(sub.quantile(.2),sub.quantile(.8)),"is_hot"]=True
            df.loc[m & ((df["출처"]=="해외")|df["is_new"]),"is_trending"]=True
        return df
    return pd.DataFrame()

@st.cache_data
def load_trend():
    if not os.path.exists("trend_data.csv"): return pd.DataFrame()
    df = pd.read_csv("trend_data.csv", encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df

df_all = load_data(); df_trend = load_trend()
if df_all.empty:
    st.error("데이터 파일이 없어요. 먼저 아래 명령어를 실행하세요.")
    st.code("python multi_crawler.py")
    st.stop()

with st.sidebar:
    st.markdown("## 👗 필터")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">플랫폼</div>', unsafe_allow_html=True)
    pf_avail = sorted(df_all["플랫폼"].unique().tolist())
    sel_pf   = st.multiselect("플랫폼", pf_avail, default=pf_avail, label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">국가 / 출처</div>', unsafe_allow_html=True)
    src_avail = sorted(df_all["출처"].unique().tolist())
    sel_src   = st.multiselect("출처", src_avail, default=src_avail, label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">검색 키워드</div>', unsafe_allow_html=True)
    kw_pool = sorted(df_all[df_all["출처"].isin(sel_src)]["검색키워드"].unique())
    sel_kws = st.multiselect("키워드", kw_pool, default=kw_pool, label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">가격 범위 (원)</div>', unsafe_allow_html=True)
    p_min,p_max = int(df_all["최저가"].min()), max(int(df_all["최저가"].max()),200000)
    price_range = st.slider("가격",p_min,p_max,(p_min,p_max),step=1000,format="%d원",label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">배지 필터</div>', unsafe_allow_html=True)
    show_hot=st.checkbox("🔴 HOT만"); show_trnd=st.checkbox("🟠 TRENDING만"); show_new=st.checkbox("🔵 NEW만")
    st.markdown("---")
    st.markdown('<div class="sb-lbl">갤러리 열 수</div>', unsafe_allow_html=True)
    col_n = st.slider("열",2,5,3,label_visibility="collapsed")
    st.markdown("---")
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear(); st.rerun()

df = df_all[
    df_all["플랫폼"].isin(sel_pf) & df_all["출처"].isin(sel_src) &
    df_all["검색키워드"].isin(sel_kws) & df_all["최저가"].between(price_range[0],price_range[1])
].copy().reset_index(drop=True)
if show_hot:  df = df[df["is_hot"]].reset_index(drop=True)
if show_trnd: df = df[df["is_trending"]].reset_index(drop=True)
if show_new:  df = df[df["is_new"]].reset_index(drop=True)

st.markdown('<div class="dash-title">👗 아동복 트렌드 대시보드</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dash-sub">8개 플랫폼 통합 · {datetime.now().strftime("%Y.%m.%d 기준")}</div>', unsafe_allow_html=True)

st.markdown('<div class="sec-head">🌐 플랫폼 바로가기</div>', unsafe_allow_html=True)
tiles = '<div class="platform-grid">'
for p in PLATFORMS:
    tiles += f'<a class="ptile" href="{p["url"]}" target="_blank" style="background:#{p["color"]}18;border-color:#{p["color"]}33"><div class="ptile-icon" style="background:#{p["color"]}">{p["icon"]}</div><div><div class="ptile-name">{p["name"]}</div><div class="ptile-sub">{p["sub"]}</div></div></a>'
tiles += '</div>'
st.markdown(tiles, unsafe_allow_html=True)
st.markdown('<hr class="div">', unsafe_allow_html=True)

if not df_trend.empty:
    st.markdown('<div class="sec-head">📈 검색 트렌드 추이 (최근 3개월)</div>', unsafe_allow_html=True)
    t_kws = [k for k in sel_kws if k in df_trend["키워드"].unique()] or df_trend["키워드"].unique().tolist()
    dft   = df_trend[df_trend["키워드"].isin(t_kws)]
    fig   = px.line(dft,x="날짜",y="검색량",color="키워드",markers=True,
                    color_discrete_sequence=["#4a6cf7","#ff6b9d","#ffa726","#26c6da","#66bb6a"],
                    labels={"날짜":"","검색량":"검색 지수","키워드":""})
    fig.update_traces(line_width=2,marker_size=4)
    fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",margin=dict(t=5,b=20,l=0,r=0),
                      xaxis=dict(showgrid=False,tickfont_size=11),yaxis=dict(gridcolor="#f5f5f5",tickfont_size=11),
                      legend=dict(orientation="h",y=1.08,x=0,font_size=11),hovermode="x unified")
    st.plotly_chart(fig,use_container_width=True)
    latest=dft["날짜"].max(); prev=latest-timedelta(weeks=2)
    ls=dft[dft["날짜"]==latest].set_index("키워드")["검색량"]; ps=dft[dft["날짜"]==prev].set_index("키워드")["검색량"]
    common=ls.index.intersection(ps.index)
    if not common.empty:
        chg=((ls[common]-ps[common])/(ps[common]+1)*100).sort_values(ascending=False)
        top=chg[chg>0].head(3)
        if not top.empty:
            badges=" ".join([f'<span style="background:#fff0f3;border:0.5px solid #ffccd5;color:#cc3333;border-radius:20px;padding:2px 9px;font-size:.75rem;font-weight:600">▲ {k} +{v:.0f}%</span>' for k,v in top.items()])
            st.markdown(f'<div style="margin:-6px 0 10px;font-size:.78rem;color:#aaa">급상승: {badges}</div>',unsafe_allow_html=True)

st.markdown('<hr class="div">', unsafe_allow_html=True)
c1,c2,c3,c4,c5=st.columns(5)
for col,lbl,val,sub in [
    (c1,"총 상품",f"{len(df):,}개",f"전체 {len(df_all):,}개"),
    (c2,"평균가",f"{int(df['최저가'].mean()):,}원" if len(df) else "—","필터 기준"),
    (c3,"HOT",f"{int(df['is_hot'].sum())}개","인기 가격대"),
    (c4,"브랜드",f"{df['브랜드'].nunique()}개","개 브랜드"),
    (c5,"플랫폼",f"{df['플랫폼'].nunique()}개","개 플랫폼"),
]:
    with col:
        st.markdown(f'<div class="kpi-wrap"><div class="kpi-l">{lbl}</div><div class="kpi-v">{val}</div><div class="kpi-s">{sub}</div></div>',unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)
st.markdown('<div class="sec-head">📊 트렌드 분석</div>', unsafe_allow_html=True)
tab1,tab2,tab3,tab4=st.tabs(["키워드별","플랫폼별","가격 분포","국내 vs 해외"])
CS=dict(plot_bgcolor="white",paper_bgcolor="white",margin=dict(t=5,b=5,l=0,r=0))
with tab1:
    if len(df):
        d=df["검색키워드"].value_counts().reset_index(); d.columns=["키워드","수"]
        fig=px.bar(d,x="키워드",y="수",color="키워드",text="수",color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition="outside",marker_line_width=0)
        fig.update_layout(**CS,showlegend=False,yaxis=dict(gridcolor="#f5f5f5"),xaxis=dict(title=""))
        st.plotly_chart(fig,use_container_width=True)
with tab2:
    if len(df):
        d=df["플랫폼"].value_counts().reset_index(); d.columns=["플랫폼","수"]
        cm={r["플랫폼"]:"#"+str(r["플랫폼색상"]) for _,r in df[["플랫폼","플랫폼색상"]].drop_duplicates().iterrows()}
        fig=px.bar(d,x="플랫폼",y="수",color="플랫폼",text="수",color_discrete_map=cm)
        fig.update_traces(textposition="outside",marker_line_width=0)
        fig.update_layout(**CS,showlegend=False,yaxis=dict(gridcolor="#f5f5f5"),xaxis=dict(title=""))
        st.plotly_chart(fig,use_container_width=True)
with tab3:
    if len(df):
        fig=px.histogram(df[df["최저가"]>0],x="최저가",nbins=25,color_discrete_sequence=["#a78bfa"])
        fig.update_layout(**CS,bargap=0.05,xaxis=dict(title="가격(원)",gridcolor="#f5f5f5"),yaxis=dict(gridcolor="#f5f5f5"))
        st.plotly_chart(fig,use_container_width=True)
with tab4:
    if len(df):
        d=df.groupby("출처").agg(상품수=("상품명","count"),평균가=("최저가","mean")).reset_index()
        d["평균가"]=d["평균가"].astype(int)
        fig=px.bar(d,x="출처",y="상품수",color="출처",text="상품수",color_discrete_map={"국내":"#4a6cf7","해외":"#111111"})
        fig.update_traces(textposition="outside",marker_line_width=0)
        fig.update_layout(**CS,showlegend=False,yaxis=dict(gridcolor="#f5f5f5"),xaxis=dict(title=""))
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(d.rename(columns={"상품수":"상품 수","평균가":"평균가(원)"}),hide_index=True,use_container_width=True)

st.markdown('<hr class="div">', unsafe_allow_html=True)
gl,gr=st.columns([4,1])
with gl:
    st.markdown(f'<div class="sec-head">🖼️ 상품 갤러리 <span style="font-size:.78rem;font-weight:400;color:#bbb">{len(df):,}개</span></div>',unsafe_allow_html=True)
with gr:
    sort_opt=st.selectbox("정렬",["기본순","가격 낮은순","가격 높은순"],label_visibility="collapsed")

df_g=(df.sort_values("최저가",ascending=(sort_opt=="가격 낮은순")).reset_index(drop=True)
      if sort_opt!="기본순" else df.copy())

if not len(df_g):
    st.warning("필터 조건에 맞는 상품이 없어요.")
else:
    cols=st.columns(col_n,gap="small")
    for idx,row in df_g.iterrows():
        with cols[idx%col_n]:
            badges=(""+('<span class="b-hot">HOT</span>' if row.get("is_hot") else "")
                      +('<span class="b-trend">TRENDING</span>' if row.get("is_trending") else "")
                      +('<span class="b-new">NEW</span>' if row.get("is_new") else ""))
            img_html=(f'<img src="{row["이미지URL"]}" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=noimg>👗</div>\'">'
                      if row["이미지URL"] else '<div class="noimg">👗</div>')
            price_str=f"{int(row['최저가']):,}원" if row["최저가"]>0 else "—"
            brand_str=row["브랜드"] if row["브랜드"]!="브랜드 없음" else ""
            pf_color="#"+str(row.get("플랫폼색상","888888"))
            tag_bg=f"#{'00006622' if row.get('출처')=='해외' else '4a6cf722'}"
            tag_color="#"+("000066" if row.get("출처")=="해외" else "3346cc")
            st.markdown(f"""
            <div class="pcard">
              <div class="pimg-wrap">{img_html}
                <div class="pbadges">{badges}</div>
                <div class="psrc-pill" style="background:{pf_color}">{row.get('플랫폼','')}</div>
              </div>
              <div class="pinfo">
                <span class="ptag" style="background:{tag_bg};color:{tag_color}">{'🌏 ' if row.get('출처')=='해외' else ''}{row['검색키워드']}</span>
                <div class="pname">{row['상품명']}</div>
                {"<div class='pbrand'>"+brand_str+"</div>" if brand_str else ""}
                <div class="pprice">{price_str}</div>
                <div class="pmall">🏪 {row['판매처']}</div>
              </div>
            </div>""",unsafe_allow_html=True)
            if row["판매처링크"]:
                st.link_button("🔗 바로가기", row["판매처링크"], use_container_width=True)
            st.markdown("<div style='margin-bottom:4px'></div>",unsafe_allow_html=True)

st.markdown('<hr class="div">', unsafe_allow_html=True)
with st.expander("📋 전체 데이터 테이블 / CSV 다운로드"):
    show_cols=["플랫폼","출처","검색키워드","상품명","최저가","브랜드","판매처","수집일시"]
    avail=[c for c in show_cols if c in df_g.columns]
    st.dataframe(df_g[avail],use_container_width=True,hide_index=True)
    st.download_button("⬇️ CSV 다운로드",df_g.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),"kids_trend.csv","text/csv")
st.markdown('<div style="text-align:center;color:#ddd;font-size:.7rem;padding:1.5rem 0 .5rem">아동복 트렌드 대시보드 v3 · 8개 플랫폼 통합</div>',unsafe_allow_html=True)
