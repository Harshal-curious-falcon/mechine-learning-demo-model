import random
import string
import nltk
from newspaper import Article
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from googletrans import Translator
import pyttsx3
import os
import requests



# Download necessary NLTK resources
nltk.download('punkt', quiet=True)

# Unsplash API access key (replace 'YOUR_ACCESS_KEY' with your actual API key)
UNSPLASH_ACCESS_KEY = 'Dsg0gm2PV1ajlinh9MTxiUYej05kokgcZ7ijRAMRKYY'

# News API access key (replace 'YOUR_NEWS_API_KEY' with your actual API key)
NEWS_API_KEY = 'fbf718f6b2134206ba8d0ff1aa1e3e4a'


# Function to fetch images related to agriculture from Unsplash
def fetch_agriculture_images():
    url = f'https://api.unsplash.com/photos/random?query=agriculture&client_id={UNSPLASH_ACCESS_KEY}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            image_url = data['urls']['regular']
            return image_url
        else:
            print(f"Failed to fetch image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching image: {e}")


# Function to fetch agriculture news from News API
def fetch_agriculture_news(count=2):
    url = f'https://newsapi.org/v2/everything?q=agriculture&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data['articles']
        random.shuffle(articles)          # Fetch only the top 2 news headlines
        return articles[:count]
    else:
        print('Failed to fetch news articles')
        return []


# Function to fetch sentences from given URLs
def fetch_sentences(urls):
    all_sentence_list = []
    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
            text = article.text
            sentence_lists = sent_tokenize(text)
            all_sentence_list.extend(sentence_lists)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            print("-----------------------------------------------------------------------------")
    return all_sentence_list


# Function to handle greetings
def greeting_response(text, language):
    text = text.lower()
    if language == 'english':
        bot_greetings = ['Howdy', 'Hi', 'Hey', 'Hello', 'Hola']
        user_greetings = ['hi', 'hello', 'greetings', 'wassup']
    elif language == 'hindi':
        bot_greetings = ['नमस्ते', 'हाय', 'नमस्कार', 'हेलो', 'कैसे हो']
        user_greetings = ['namaste', 'heelo', 'namaskar', 'aadab', 'kyahaal hai']
    else:
        return "I'm sorry, I couldn't understand your language choice."

    for word in text.split():
        if word in user_greetings:
            return random.choice(bot_greetings)


# Function to generate response based on user input
def agitech_response(user_input, sentence_list, language):
    user_input = user_input.lower()
    sentence_list.append(user_input)
    response = ''
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(sentence_list)
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    similar_sentence_index = cosine_similarities.argsort()[0][-2]
    similar_sentences = cosine_similarities.flatten()
    similar_sentences.sort()
    response_flag = 0
    if similar_sentences[-2] == 0:
        response = "I apologize, I don't understand."
    else:
        response = sentence_list[similar_sentence_index]
        if language == 'hindi':
            try:
                translator = Translator()
                response = translator.translate(response, src='en', dest='hi').text
            except Exception as e:
                print(f"Error translating: {e}")
    sentence_list.remove(user_input)
    return response


# Main function to drive the chatbot
def chatbot(urls, user_history=None):
    if user_history is None:
        user_history = []  # Initialize user history list

    print(
        'agitech bot: I am an agitech bot, here to find your best answer possible for your problems from provided context.')
    language = input("Choose language (english/hindi): ").lower()
    while language not in ['english', 'hindi']:
        print("Invalid language choice! Please choose between English and Hindi.")
        language = input("Choose language (english/hindi): ").lower()
    exit_list = ['exit', 'see you later', 'bye', 'quit']
    sentence_list = fetch_sentences(urls)
    while True:
        user_input = input('You: ')
        user_history.append(user_input)  # Add user input to history
        if user_input.lower() in exit_list:
            print('agitech bot: Chat with you later!')
            break
        else:
            greeting = greeting_response(user_input, language)
            if greeting:
                print('agitech bot: ' + greeting)
            elif user_input.lower() == 'news':  # Check if user wants to see news headlines
                articles = fetch_agriculture_news()
                if articles:
                    print("Latest Agriculture News Headlines:")
                    for idx, article in enumerate(articles, start=1):
                        print(f"{idx}. {article['title']} - {article['source']['name']}")
                else:
                    print("No news articles available.")
            else:
                response = agitech_response(user_input, sentence_list, language)
                print('agitech bot: ' + response)
                # Fetch and display image related to agriculture
                image_url = fetch_agriculture_images()
                if image_url:
                    print(f'Image: {image_url}')

    # Optionally, you can print or store the user history after the conversation ends
    print("User History:")
    for idx, interaction in enumerate(user_history, start=1):
        print(f"{idx}. {interaction}")


# URLs for fetching information
urls = [
    "https://en.wikipedia.org/wiki/Agriculture_in_India",
    "https://eos.com/blog/crop-diseases/",
    "https://education.nationalgeographic.org/resource/crop/",
    "https://www.plugandplaytechcenter.com/resources/new-agriculture-technology-modern-farming/",
    "https://www.jiva.ag/blog/what-are-the-most-common-problems-and-challenges-that-farmers-face",
    "https://timesofindia.indiatimes.com/india/empowering-indias-farmers-list-of-schemes-for-welfare-of-farmers-in-india/articleshow/107854121.cms"
]

# Run the chatbot with user history
chatbot(urls)





