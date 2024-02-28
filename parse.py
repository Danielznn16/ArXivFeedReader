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

def convert_title_string(title_string):
	# Extracting the title content up to the arXiv identifier
	match = re.match(r"(.+?)\s\((arXiv:.+?)\s\[(.+?)\].*?\)", title_string)
	if match:
		title, _, tag = match.groups()
	return (title, tag)


def clean_entry(feed_entry):
	feed_entry['author'] = clean_html(feed_entry['author'])
	feed_entry['summary'] = clean_html(feed_entry['summary']).replace("\n- ","").replace("\n"," ").replace("  ", " ")
	feed_entry["title"], feed_entry["tag"] = convert_title_string(feed_entry.title)
	del feed_entry["summary_detail"], feed_entry["links"], feed_entry["title_detail"], feed_entry["author_detail"], feed_entry["authors"]
	return feed_entry

def convert_data(source_data):
	target_data = {}
	
	target_data['link'] = source_data['link']
	target_data['abstract'] = source_data['summary']
	target_data['authors'] = source_data['author']
	
	# Convert the tags into the desired format
	target_data[source_data["tag"]] = True
	# target_data['cs'] = {source_data['tag']: True}
	
	# Convert the time.struct_time into the desired string format
	updated_date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', source_data['updated'])
	target_data['date'] = updated_date
	
	email_date = time.strftime('%Y-%m-%d', source_data['email_date'])
	target_data['email_date'] = email_date
	
	# Transform the id into the desired format
	arxiv_id = source_data['id'].split('/')[-1]
	target_data['id'] = f"arXiv:{arxiv_id}"
	
	target_data['title'] = source_data['title']
	
	return target_data

# Connect to your MongoDB instance
client = MongoClient()
collection = client.mail.arxiv

from pprint import pprint
# Parse the RSS feed
rss_feed_urls = ['https://export.arxiv.org/rss/cs.CL']
def parse():
	for rss_feed_url in rss_feed_urls:
		feed = feedparser.parse(rss_feed_url)
		time = feed.feed.updated_parsed
		for entry in feed.entries:
			try:
				raw_title = entry.title
				entry = clean_entry(entry)
				entry["date"] = time
				entry["email_date"] = time
				entry = convert_data(entry)
				entry["ParserVer"] = "2.0"
				if entry["id"]+"v1 " not in raw_title:
					del entry["email_date"]
					# print(raw_title)
				else:
					print(entry["id"])
				collection.update_one(dict(id=entry["id"]),{"$set":entry},upsert=True)
			except:
				pass

parse()

while True:
	try:
		parse()
	except:
		pass
	time.sleep(4 * 60 * 60)  # Sleeps for 4 hours
