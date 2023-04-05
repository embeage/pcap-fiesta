import argparse
import json
import os
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from webdriver_manager.chrome import ChromeDriverManager


def svt_play_video(video_id, url, playback_time, save_requests=False, exit_flag=None):

    os.environ['WDM_LOG'] = '0'
    options = webdriver.ChromeOptions()
    options.add_argument('--log-level=3')
    options.add_argument('start-maximized')
    driver = webdriver.Chrome(ChromeDriverManager().install(),
                              options=options)
    driver.get(url)

    # Click cookie pop-up
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Acceptera alla']"))
        ).click()
    except TimeoutException:
        pass
    else:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element(
                (By.XPATH, "//div[@role='dialog' and contains(" +
                    "@aria-label, 'cookies')]")))

    # Play video
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[starts-with(@aria-label, 'Spela') " +
                    "and starts-with(text(), 'Spela')]"))
        ).click()
    except TimeoutException:
        if exit_flag is not None:
            exit_flag.set()
        else:
            driver.quit()
            return

    # Accept inappropriate content
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='Jag förstår']"))
        ).click()
    except TimeoutException:
        pass
    else:
        driver.find_element(By.XPATH,
            "//button[@data-rt='video-player-parental-splash-play']").click()

    # Will maybe get another play prompt, if so, click it.
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-rt='video-player-splash-play']"))
        ).click()
    except TimeoutException:
        pass

    if exit_flag is not None:
        while not exit_flag.is_set():
            exit_flag.wait(playback_time)
            exit_flag.set()
    else:
        time.sleep(playback_time)

    if save_requests:
        segment_requests = []
        for request in driver.requests:
            if request.method == 'GET' and request.url.endswith('.mp4'):
                response = request.response
                if response is None:
                    continue
                get_request = {
                    'segment_url': request.url,
                    'content_length': response.headers.get('Content-Length'),
                    'date': request.date.strftime("%Y-%m-%d %H:%M:%S.%f")
                }
                segment_requests.append(get_request)

        with open(f"requests/{video_id}.json", 'w', encoding='utf-8') as json_file:
            json.dump(segment_requests, json_file, indent=4)

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Opens a Chrome window and plays a SVT Play video.")
    parser.add_argument('--id',
                        help="SVT Play video ID",
                        required=True)
    parser.add_argument('--url', required=True)
    parser.add_argument('--time',
                        help="How long to play the video in seconds.",
                        required=True)
    parser.add_argument('--save-requests',
                        help="Save GET requests for segments to a file.",
                        action='store_true')
    args = parser.parse_args()
    svt_play_video(args.id, args.url, int(args.time), save_requests=args.save_requests)
