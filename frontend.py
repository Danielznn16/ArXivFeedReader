import streamlit as st
#st.set_page_config(layout="wide")
from utils import *
from mongo import arxiv_db

st.set_page_config(page_title="Arxiv", page_icon="./icon.jpg")

def getDates():
	unreadOnly = st.selectbox(
		"未读/已读/Star/所有",
		options=[
			dict(value={"$exists":False},label="未读"), # UnRead Only
			dict(value={"$exists":True},label="已读"), # Already Read
			dict(value="Star",label="标星⭐️"), # Starred
			dict(value=False,label="All") # All
			],
		format_func=lambda x:x["label"],
		index=0)["value"]
	if unreadOnly:
		num = arxiv_db.count_documents({"Read":unreadOnly})
		dates = sorted(arxiv_db.find({"Read":unreadOnly}).distinct("email_date"),reverse=False)
	else:
		num = arxiv_db.count_documents({})
		dates = sorted(arxiv_db.find({}).distinct("email_date"),reverse=False)
	st.markdown(f"**{num}** Papers in List")
	k = st.select_slider("选择日期",dates,value=dates[-1])
	return k,unreadOnly

def MarkRead(paper_id):
	arxiv_db.update_one(dict(_id=paper_id),{"$set":{"Read":"Read"}})

def MarkStar(paper_id):
	arxiv_db.update_one(dict(_id=paper_id),{"$set":{"Read":"Star"}})

def getPapers(date,unreadOnly):
	query = dict(email_date=date)
	is_first = True
	papers = list(arxiv_db.find(query))
	read_cnt = 0
	total = len(papers)
	for paper in papers:
		if "Read" in paper:
			read_cnt+=1
	st.progress(read_cnt/total,text=f"{read_cnt} Read in {total}")
	if unreadOnly:
		query["Read"] = unreadOnly
		papers = list(arxiv_db.find(query))
	for paper in papers:
		raw_title = paper["title"]
		if "Read" in paper:
			if paper["Read"]=="Star":
				paper["title"] = "\\[标星⭐️\\] "+f"*{paper['title']}*"
			else:
				paper["title"] = "\\[已读\\] "+f"*{paper['title']}*"
		else:
			paper["title"] = "\\[未读\\] "+f"*{paper['title']}*"
		with st.expander(paper["title"],is_first):
			is_first = False
			paper_id = paper["_id"]
			l,r=st.columns(2)
			l.button(
				"Mark → 已读",
				on_click=MarkRead,
				key=paper["link"]+"read",
				use_container_width=True,
				kwargs=dict(paper_id=paper_id),
				disabled=("Read" in paper)
				)
			r.button(
				"Mark → 标星⭐️",
				on_click=MarkStar,
				key=paper["link"]+"star",
				use_container_width=True,
				kwargs=dict(paper_id=paper_id),
				disabled=("Read" in paper and paper["Read"]=="Good")
				)
			st.markdown(f"### {raw_title}")
			st.markdown("###### [View in arXiv]({})".format(paper["link"].replace("abs","pdf")+".pdf"))
			for key,value in sorted(list(paper.items()),key=lambda x:x[0]):
				if key in ["_id","link","email_date","title","cs","Read"]:
					continue
				st.markdown(f"###### {key}")
				if key=="abstract":
					value = value.replace(". ",".\n\n")
				st.markdown(
					value if value is not str else bionic_reading(value),
					unsafe_allow_html=True)
			if "cs" in paper:
				st.markdown(f"###### tags(under cs)")
				st.markdown(', '.join(list(paper["cs"].keys())))
date,unreadOnly = getDates()
getPapers(date,unreadOnly)
