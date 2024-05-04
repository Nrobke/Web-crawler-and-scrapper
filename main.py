import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import re

# Download NLTK data (only required once)
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")


def get_nouns(text):
    # Tokenize the text into words
    words = word_tokenize(text)

    # Tag the words with their parts of speech
    tagged_words = pos_tag(words)

    # Filter out only nouns
    nouns = [word for word, pos in tagged_words if pos.startswith("N")]

    return nouns


def filter_valid_words(text):
    words = word_tokenize(text)

    valid_word_pattern = re.compile(r"^[a-zA-Z]+$")

    valid_words = ",".join([word for word in words if valid_word_pattern.match(word)])

    return valid_words


def get_words_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract words from the text content of the page
    words = ",".join([word.lower() for word in soup.get_text().split()])
    title = url
    try:
        titleHeader = soup.find(name="h1", id="firstHeading")
        if titleHeader != None:
            title = titleHeader.text
        elif titleHeader == None:
            titleHeader = soup.find(name="div", class_="mt-50")
            if titleHeader != None:
                title = titleHeader.text.strip("\n")
        else:
            titleHeader = soup.find(name="a", class_="breadcrumb-item active")
            if titleHeader != None:
                title = titleHeader.text
    except:
        pass
    return {
        "site": url,
        "title": title,
        "content": get_nouns(filter_valid_words(words)),
    }


def crawl_website(start_url, depth):
    visited_urls = set()

    def recursive_crawl(url, current_depth):
        if current_depth > depth or url in visited_urls:
            return

        print(f"started : {url}")
        visited_urls.add(url)
        parsed = get_words_from_page(url)

        # Save the information in JSON format
        result.append(parsed)

        # Extract links from the page and recursively crawl them
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            next_url = urljoin(url, link["href"])
            valid_domain = next_url.startswith(
                "https://en.wikipedia.org/wiki/"
            ) or next_url.startswith("https://whc.unesco.org/en/") or next_url.startswith("https://ich.unesco.org/en/")

            if valid_domain:
                try:
                    recursive_crawl(next_url, current_depth + 1)
                except:
                    pass

    result = []
    recursive_crawl(start_url, 0)

    return result


if __name__ == "__main__":
    start_address = input("Enter the starting web address: ")
    depth_limit = int(input("Enter the depth limit: "))

    result_data = crawl_website(start_address, depth_limit)

    # Save the result in a JSON file
    with open("web_crawling_result_1.json", "w") as json_file:
        json.dump(result_data, json_file, indent=2)

    print("Web crawling completed. Result saved in 'web_crawling_result.json'.")
