import feedparser
from pymongo import MongoClient
from bs4 import BeautifulSoup
import html
import re

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

# Connect to your MongoDB instance
# client = MongoClient('localhost', 27017)
# db = client['rss_database']  # Choose your database name
# collection = db['rss_items']  # Choose your collection name

# Parse the RSS feed
rss_feed_url = 'https://export.arxiv.org/rss/cs.CL'
def parse():
	feed = feedparser.parse(rss_feed_url)
	time = feed.feed.updated_parsed
	for entry in feed.entries:
		# try:
			entry = clean_entry(entry)
			entry.date = time
			# break
		# except:
		# 	pass
			# collection.insert_one(item)

parse()