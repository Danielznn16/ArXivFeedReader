import feedparser
from pymongo import MongoClient
from bs4 import BeautifulSoup
import html
import re
import time

def clean_html(html_content):
	"""Remove HTML tags and return plain text."""
	soup = BeautifulSoup(html_content, "html.parser")
	return html.unescape(soup.get_text())


def clean_entry(feed_entry):
	cleaned_entry = dict()
	cleaned_entry["title"] = clean_html(feed_entry.title)
	cleaned_entry['authors'] = clean_html(feed_entry.author_detail["name"])
	summary_header, abstract = feed_entry.summary.split("\n")[0], "\n".join(feed_entry.summary.split("\n")[1:])
	cleaned_entry['abstract'] = abstract
	cleaned_entry["link"] = feed_entry.link
	cleaned_entry["tag"] = [tag["term"] for tag in feed_entry.tags]
	cleaned_entry["id"] = feed_entry.id.split("arXiv.org:")[-1]
	cleaned_entry["status"] = summary_header.split("Announce Type: ")[-1].strip()
	# feed_entry["title"], feed_entry["tag"] = convert_title_string(feed_entry.title)
	# del feed_entry["summary_detail"], feed_entry["links"], feed_entry["title_detail"], feed_entry["author_detail"], feed_entry["authors"]
	return cleaned_entry

def convert_data(source_data):
	target_data = {}
	
	target_data['link'] = source_data['link']
	target_data['abstract'] = source_data['abstract']
	target_data['authors'] = source_data['authors']
	
	# Convert the tags into the desired format
	for tag in source_data['tag']:
		target_data[tag] = True
	# target_data['cs'] = {source_data['tag']: True}
	
	# Convert the time.struct_time into the desired string format
	updated_date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', source_data['date'])
	target_data['date'] = updated_date
	
	email_date = time.strftime('%Y-%m-%d', source_data['email_date'])
	target_data['email_date'] = email_date
	
	# Transform the id into the desired format
	arxiv_id = source_data['id']
	target_data['id'] = f"arXiv:{arxiv_id}"
	
	target_data['title'] = source_data['title']
	
	return target_data

# Connect to your MongoDB instance
client = MongoClient()
collection = client.mail.arxiv

from pprint import pprint
# Parse the RSS feed
rss_feed_urls = ['http://rss.arxiv.org/rss/cs.CL']
def parse():
	for rss_feed_url in rss_feed_urls:
		feed = feedparser.parse(rss_feed_url)
		time = feed.feed.updated_parsed
		for entry in feed.entries:
			try:
			# if True:
				entry = clean_entry(entry)
				entry["date"] = time
				entry["email_date"] = time
				status = entry["status"]
				entry = convert_data(entry)
				entry["ParserVer"] = "2.1"
				if status!="new":
					del entry["email_date"], entry["date"]
				pprint(entry)
				collection.update_one(dict(id=entry["id"]),{"$set":entry},upsert=True)
			except Exception as e:
				print(e)

parse()

while True:
	try:
		parse()
	except:
		pass
	time.sleep(23 * 60 * 60)  # Sleeps for 4 hours
