import os

import requests
from dotenv import load_dotenv


class oMessage:
    def __init__(self, content: str):
        self.content = content

    def parse(self):
        return {
            "type": "text",
            "text": self.content
        }


class oImage(oMessage):
    # @classmethod
    # def image_data_to_base64_str(cls, image_data: str):
    #     image_data_base64 = re.sub('^data:image/.+;base64,', '', image_data)
    #     image_bytes = base64.b64decode(image_data_base64)
    #     resized_image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    def parse(self):
        return {
            "type": "image_url",
            "image_url": {
                # "url": f"data:image/jpeg;base64,{self.content}"
                "url": self.content
            }
        }


class OpenAIClient:
    def __init__(self):
        load_dotenv()
        OPENAI_KEY = os.getenv("OPENAI_KEY")
        if not OPENAI_KEY:
            raise Exception("API_KEY not found in .env file")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_KEY}"
        }

    def send_message(self, *messages: oMessage, raw: bool = False):
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [msg.parse() for msg in messages]
                }
            ],
            "max_tokens": 300
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)
        res = response.json()
        print(res)
        if raw:
            return res
        else:
            return res["choices"][0]["message"]["content"]

    def write_letter(self, issue: str, title: str, name: str, address: str):
        prompt = f"""
            You are a helpful assistant that assists in writing letters to local politicians. Please write a formal, concise, 2-paragraph letter addressing the issue of {issue}. State that I encountered the issue at {address}. Emphasize the seriousness of the problem and how it poses potential harm to municipal citizens like myself. Highlight why a problem like {issue} would be. 

            Convey that I trust public officials like {title} {name} to address and resolve these issues for the benefit of the community. Format the letter appropriately for email communication to a politician, ensuring it is professional and concise.
            """

        return self.send_message(
            oMessage(prompt)
        )

    def send_camera(self, image_data: str):
        prompt = f"""
            Return me two pieces of information, separated by a pipe | symbol.
            You are looking in the following image for these features: [pothole, sidewalk, streetlight], in this order of importance.
            1) In one word, return the most important feature that was discovered e.g. pothole
            2) A short comment to help a user identify the most important feature e.g. "A pothole in the middle of the road, roughly 1m wide"
        """
        return self.send_message(
            oMessage(prompt),
            oImage(image_data)
        )

    def tweet_sentiment(self, tweet: str):
        prompt = f"""
            I am giving you a tweet from a person commenting on issues in their local area. You will give me a score of the sentiment between 
            1 - 10, where 1 is very negative, 10 is very positive, and 5 is neutral. Return only a single number with nothing else. 
        """
        return self.send_message(
            oMessage(prompt),
            oMessage(tweet)
        )

if __name__ == "__main__":
    # Example usage
    issue = "potholes"
    title = "Senator"
    name = "Jane Doe"

    OpenAIClient().write_letter(issue, title, name)
