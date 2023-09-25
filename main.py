from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def initialize_driver(chromedriver_path: str):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_service = ChromeService(chromedriver_path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    return driver


def navigate_to_url(driver, url: str):
    print(f"Navigating to {url}...")
    driver.get(url)


def find_video_list(driver):
    try:
        video_list = driver.find_element(
            By.XPATH,
            "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]",
        )
        if video_list:
            print("Video list found.")
            return video_list
        else:
            print("Video list not found.")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def extract_titles(driver, url):
    # Check if the URL is for YouTube
    if url.startswith("https://www.youtube.com/"):
        # Navigate to the URL
        navigate_to_url(driver, url)

        # Find the video list
        video_list = find_video_list(driver)

        if video_list:
            # Find all video elements within the parent element
            video_elements = video_list.find_elements(By.XPATH, ".//ytd-video-renderer")

            titles_list = []

            for video_element in video_elements:
                # Extract the title text from the video element
                title_element = video_element.find_element(
                    By.XPATH, ".//a[@id='video-title']"
                )
                title = title_element.get_attribute("title")
                titles_list.append({"title": title})

            return titles_list
        else:
            print("No video list found.")
            return []
    else:
        print("Error: Invalid URL.")
        return []


def query_transcripts(titles: str, search_string: str):
    """Queries the transcripts for a specific term."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Generate engaging YouTube video titles based on the top-performing titles for a given youtube video category. The user has provided a search string for the video they want to make and an array of top performing video titles. You should analyze the top video titles and generate creative and attention-grabbing titles that are likely to increase viewership and engagement. Consider using persuasive language, keywords, and appealing themes to attract a wider audience. Keep the titles concise and relevant to the content. Remember that the goal is to captivate viewers and encourage them to click on the video. Generate multiple title options for the user to choose from, ensuring they are catchy and aligned with the user's content.",
            },
            {
                "role": "user",
                "content": "Desired video theme: "
                + search_string
                + "\n\n"
                + "Top Performing video titles: "
                + titles,
            },
        ],
        temperature=1,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    response = response.choices[0].message.content
    return response


def input_to_search_string(input_string):
    search_string = input_string.replace(" ", "+")
    return search_string


def main():
    # Define the URL and path to Chromedriver
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")

    # Initialize WebDriver
    driver = initialize_driver(chromedriver_path)

    # Get video description from user input
    video_description = input("Enter a video search query: ")
    video_search_string = input_to_search_string(video_description)

    # Extract titles from a YouTube search results page
    titles_list = extract_titles(
        driver, f"https://www.youtube.com/results?search_query={video_search_string}"
    )

    titles_arr = []
    for title in titles_list:
        titles_arr.append(title["title"])

    better_titles = query_transcripts(str(titles_arr), video_description)
    print(better_titles)

    # Close the WebDriver
    driver.quit()


if __name__ == "__main__":
    main()
