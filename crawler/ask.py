from bs4 import BeautifulSoup
import os
import json
import requests
import logging
import time

class AskPostInfo:

    def __str__(self):
        return f"question: {self.question}\ndescription:{self.description}"

    def __init__(self, ask_id:int, question: str, description: str):
        self.ask_id = ask_id
        self.question = question
        self.description = description
    
    def is_empty(self) -> bool:
        return self.question == "" and self.description == ""
    
    def to_dict(self) -> dict:
        return {
            "ask_id": self.ask_id,
            "question": self.question,
            "description": self.description,
        }

class AskCrawler:

    base_URL = "https://ask.pinggu.org/"
    ask_path = "ask/"
    if not os.path.exists(ask_path):
        os.makedirs(ask_path)

    @classmethod
    def get_ask_post_info(cls, ask_id:int) -> AskPostInfo:
        request_URL = f"{cls.base_URL}q-{ask_id}.html"

        logging.info(f"Requesting Ask {ask_id}")
        while True:
            try:
                response = requests.get(request_URL)
                break
            except Exception as e:
                logging.error(f"Request Ask {ask_id} failed")
                time.sleep(1)

        soup = BeautifulSoup(response.text, 'html.parser')
        questionbox = soup.find("div", class_="questionbox")

        if questionbox is None:
            return None
         
        question = questionbox.find("div", class_="title").text.strip()
        description = questionbox.find("div", class_="description").text.strip()
        return AskPostInfo(ask_id=ask_id,
                           question=question,
                           description=description)
    
    @classmethod
    def crawl_ask(cls, start_id:int=1, end_id:int=666666, chunk_size:int=20):
        """Retrieve ask post information from id range of [start_id, end_id),
        save on every 1000 questions."""
        while start_id < end_id:
            chunk_limit = min(start_id + chunk_size, end_id)
            file_name = f"ask-from-{start_id}-to-{chunk_limit}.json"
            file_path = os.path.join(cls.ask_path, file_name)

            if not os.path.exists(file_path):
                ask_posts = []
                for ask_id in range(start_id, chunk_limit):
                    ask_post_info = cls.get_ask_post_info(ask_id)
                    if ask_post_info is not None:
                        ask_posts.append(ask_post_info.to_dict())
                        logging.info(f"Got ask_id: {ask_id}")
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(ask_posts, file, indent=4, ensure_ascii=False)
                    logging.info(f"Ask {start_id}-{chunk_limit-1} saved to :{file_path}")
            else:
                logging.info(f"{file_name} already exists.")
            start_id += chunk_size
        
def main_ask():
    logging.info("Starting crawling ask...")
    AskCrawler.crawl_ask(start_id=581)