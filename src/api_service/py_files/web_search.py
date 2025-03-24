from openai import OpenAI
import os
import openai
import time
from pprint import pprint
from bs4 import BeautifulSoup
import requests, time, shutil, threading, tempfile
from youtube_transcript_api import YouTubeTranscriptApi
import re
from serpapi import GoogleSearch

SERP_API = os.env("SERP_API")
client = os.env("Open_ai")

def generate_google_search_query(user_input):
    prompt = f"Convert the following user query into a optimized Google Search query: '{user_input}'"

    try:
        completion = client.chat.completions.create(
        model = "gpt-4-1106-preview",
        messages = 
            [
                {"role": "system", "content": "You are a Google Search Expert. Your task is to convert unstructured user inputs into optimized Google Search queries. Example: USER INPUT: 'Why was Sam Altman fired from OpenAI?' OPTIMIZED Google Search Query: 'Why Sam Altman Fired from OpenAI?'"},
                {"role": "user", "content": prompt}
            ]
        )

        #Accessing the response directly
        if completion.choices:
            response_message = completion.choices[0].message
            if hasattr(response_message, 'content'):
                return response_message.content.strip()
            else:
                return "No content in response"
        else:
            return "No response from GPT-4 Turbo."
    except Exception as e:
        print(f"Error in generating Google Search query: {e}")
        return None
    
# Function to get top URLs based on the query
def get_organic_results(query, num_results):
    params = {
        "q": query,
        "engine": "google",
        "hl": "en",
        "num": str(num_results),
        "api_key": SERP_API  # Replace with your actual SERP API key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    news_results = results.get("news_results", [])

    urls = [result['link'] for result in news_results]
    return urls

#Define the function to scrape data from a URL and return the URL 
def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, features="lxml")
        formatted_data = ' '.join(soup.text.split())
        return formatted_data
    except Exception as e:
        print(f"Error fetching URL {url}: {str(e)}")
        return "Failed to retrieve the webpage"
    

def combined_scrape_function(query, num_results=3):
    # Get URLs from the search query
    urls = get_organic_results(query, num_results)

    # Scrape and combine content from each URL
    combined_content = ''
    for url in urls:
        scraped_data = scrape_website(url)
        combined_content += scraped_data + '\n\n'  # Separate content from different URLs

    return combined_content
    
# Create an Assistant with a specific name
assistant = client.beta.assistants.create(
    name="GoogleGPT",
    instructions="You are an assistant capable of fetching and displaying news articles based on user queries.",
    model="gpt-4-1106-preview",
    tools=
        [
            {
                "type": "function",
                "function": 
                    {
                        "name": "get_organic_results",
                        "description": "Fetch web URLs based on a search query",
                        "parameters":
                            {
                                "type":"object",
                                "properties":
                                    {
                                        "query": {"type": "string", "description": "Search query"},
                                        "num_results": {"type": "integer", "description": "Number of results to return"},
                                    },
                                "required": ["query"]
                            }
                    } 

            },
            {
                "type": "function",
                "function": 
                    {
                        "name": "scrape_website",
                        "description": "Scrape the textual content from a given URL",
                        "parameters":
                            {
                                "type": "object",
                                "properties":
                                    {
                                        "url": {"type": "string", "description": "URL to scrape"}
                                    },
                                    "required": ["url"]
                            }
                    }
            }
        ]
    )


while True:
    user_query = input("Please enter your query (type 'exit' to quite): ")
    if user_query.lower() == 'exit':
        break

    google_search_query = generate_google_search_query(user_query)
    print(f"Converted Google Search Query: {generate_google_search_query}")

    if google_search_query:
        news_urls = get_organic_results(google_search_query)

        if news_urls:
            url, news_content = scrape_website(news_urls[0])

            grounding_context = f"Context: {news_content}\nUser Query: {user_query}"
            print(grounding_context)

            completion = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=
                [
                    {"role": "system", "content": "You are a helpful assistant, always return only the essential parts that answers the USER original USER query, but add 3 bullet points to backup your reasoning for the answer."},
                    {"role": "user", "content": grounding_context}
                ]
            )

            response = completion.choinces[0].message.content if completion.choices[0].message else ""
            print("Response GPT 4: ", response)

        else:
            print("No news articles")

    else:
        print("Failed to generate Google Search query.")
