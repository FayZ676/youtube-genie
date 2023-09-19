from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


def initialize_driver(chromedriver_path: str):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_service = ChromeService(chromedriver_path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    return driver


def navigate_to_url(driver, url: str):
    print(f"Navigating to {url}...")
    driver.get(url)
    return


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
    # Check if the url is prefixed by https://minnstate.zoom.us/ or https://mediaspace.minnstate.edu/
    if url.startswith("https://www.youtube.com/"):
        # Navigate to the URL
        navigate_to_url(driver, url)

        # Find the video list
        video_list = find_video_list(driver)
        video_elements = video_list.find_elements(By.XPATH, ".//ytd-video-renderer")

        titles_list = []

        for video_element in video_elements:
            # Extract the title text from the video element
            title_element = video_element.find_element(
                By.XPATH, ".//a[@id='video-title']"
            )
            title = title_element.get_attribute("title")
            titles_list.append({"title": title})

    else:
        print("Error: Invalid URL.")
        return
    return titles_list


def main():
    # Define the URL and path to Chromedriver
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")

    # Initialize WebDriver
    driver = initialize_driver(chromedriver_path)
    titles_list = extract_titles(
        driver, "https://www.youtube.com/results?search_query=crypto"
    )
    print(titles_list)

    # Close the WebDriver
    driver.quit()


if __name__ == "__main__":
    main()
