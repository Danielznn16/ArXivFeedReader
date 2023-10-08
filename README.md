# ArXivFeedReader
New Arxiv Reader base on Feed

### Install
```bash
pip3 install pymongo feedparser
```

### Run
#### MongoDB
First you should luanch a MongoDB in the default port 27017, and create a collection of `client.mail.arxiv`.

#### Parser
Luanch the parser to automatically retrieve arxiv papers.
```bash
nohup python3 parse.py
```

#### Frontend
Finally, launch your frontend by
```bash
streamlit run frontend --server.port=8080
```