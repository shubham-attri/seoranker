"""
This file contains functions and classes related to main operations
"""

from langchain_ollama.llms import OllamaLLM
from langchain.chat_models import init_chat_model
from ingestcontent import extract_markdown_from_url, search_google
import asyncio
from db import connect_db
import logging

# https://langchain-ai.github.io/langgraph/agents/agents/#1-install-dependencies (for langgraph) 
model = init_chat_model(
    "qwen3:1.7b", model_provider="ollama",
    temperature=0,
    )

# https://bestiabrisk.com/blogs/blogs/how-to-brew-the-perfect-cup-of-instant-coffee-tips-and-tricks

# Adding internal links with link like above in our markdown content for blog posts and SEO

c, conn = connect_db()

c.execute("CREATE TABLE IF NOT EXISTS crawled (keyword text, crawled integer)")
conn.commit()


c.execute("CREATE TABLE IF NOT EXISTS keywords (keyword text)")
conn.commit()

def add_keyword(keyword):
    logging.info(f"Adding keyword {keyword} to db")
    c.execute("INSERT INTO keywords (keyword) VALUES (?)", (keyword,))
    conn.commit()

def get_keywords():
    logging.info("Fetching all keywords from db")
    c.execute("SELECT keyword FROM keywords")
    return [row[0] for row in c.fetchall()]

async def scrape_keywords():
    logging.info("Fetching all keywords from db")
    keywords = get_keywords()
    logging.info(f"Found {len(keywords)} keywords")
    for keyword in keywords:
        c.execute("SELECT * FROM crawled WHERE keyword = ?", (keyword,))
        if c.fetchone():
            logging.info(f"Already crawled {keyword}")
            continue
        
        logging.info(f"Scraping {keyword}")
        results = await search_google(keyword)
        logging.info(f"Found {len(results.organic_results)} results for {keyword}")


        for result in results.organic_results:
            try:

                # logging.info(f"Checking if {keyword} is already crawled")
                # c.execute("SELECT * FROM crawled WHERE keyword = ?", (keyword,))
                # if c.fetchone():
                #     logging.info(f"Already crawled {keyword}")
                #     continue

                logging.info(f"Scraping {result['link']}")
                result = await extract_markdown_from_url(result['link'])
                if result.error:
                    logging.error(f"Error scraping {keyword}: {result.error}")
                    continue

                logging.info(f"Successfully scraped {keyword}")
                
                c.execute("INSERT INTO crawled (keyword, crawled) VALUES (?, ?)", (keyword, 1))
                conn.commit()

            except Exception as e:
                logging.error(f"Error scraping {keyword}: {e}")


logging.info("Adding keywords from keywords.txt to db")
with open("keywords.txt") as f:
    for keyword in f.readlines():
        keyword = keyword.strip()
        if keyword not in get_keywords():
            add_keyword(keyword)


asyncio.run(scrape_keywords())
