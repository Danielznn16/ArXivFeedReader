import streamlit as st
st.set_page_config(layout="wide")
from mongo import arxiv_db

def getDates():
	user = st.text_input("用户名称")
	if user=="zlnn":
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
	else:
		unreadOnly = False
	if unreadOnly:
		dates = sorted(arxiv_db.find({"Read":unreadOnly}).distinct("email_date"),reverse=False)
	else:
		dates = sorted(arxiv_db.find({}).distinct("email_date"),reverse=False)
	k = st.select_slider("选择日期",dates,value=dates[-1])
	return k,unreadOnly,user

def MarkRead(paper_id):
	arxiv_db.update_one(dict(_id=paper_id),{"$set":{"Read":"Read"}})

def MarkStar(paper_id):
	arxiv_db.update_one(dict(_id=paper_id),{"$set":{"Read":"Star"}})

def getPapers(date,unreadOnly,user):
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
			if user=="zlnn17":
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
					value,
					unsafe_allow_html=True)
			if "cs" in paper:
				st.markdown(f"###### tags(under cs)")
				st.markdown(', '.join(list(paper["cs"].keys())))
date,unreadOnly,user = getDates()
getPapers(date,unreadOnly,user)
