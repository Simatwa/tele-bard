import json
import os
import time
import urllib

import regex
import requests
import logging

BING_URL = "https://www.bing.com"


class ImageGen:
    """
    Image generation by Microsoft Bing
    Parameters:
        auth_cookie: str
    """

    def __init__(self, auth_cookie: str) -> None:
        self.session: requests.Session = requests.Session()
        self.session.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "referrer": "https://www.bing.com/images/create/",
            "origin": "https://www.bing.com",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63",
        }
        self.session.cookies.set("_U", auth_cookie)

    def get_images(self, prompt: str) -> list:
        """
        Fetches image links from Bing
        Parameters:
            prompt: str
        """
        print(">[*] Sending request...", end="\r")
        url_encoded_prompt = urllib.parse.quote(prompt)
        # https://www.bing.com/images/create?q=<PROMPT>&rt=3&FORM=GENCRE
        url = f"{BING_URL}/images/create?q={url_encoded_prompt}&rt=4&FORM=GENCRE"
        response = self.session.post(url, allow_redirects=False)
        if response.status_code != 302:
            # if rt4 fails, try rt3
            url = f"{BING_URL}/images/create?q={url_encoded_prompt}&rt=3&FORM=GENCRE"
            response3 = self.session.post(url, allow_redirects=False, timeout=200)
            if response3.status_code != 302:
                logging.error(response3.text)
            response = response3
        # Get redirect URL
        redirect_url = response.headers["Location"].replace("&nfy=1", "")
        request_id = redirect_url.split("id=")[-1]
        self.session.get(f"{BING_URL}{redirect_url}")
        # https://www.bing.com/images/create/async/results/{ID}?q={PROMPT}
        polling_url = f"{BING_URL}/images/create/async/results/{request_id}?q={url_encoded_prompt}"
        # Poll for results
        # print(">[*] Waiting for results...", end="\r")
        start_wait = time.time()
        while True:
            if int(time.time() - start_wait) > 300:
                raise Exception("Timeout error")
            # print(".", end="", flush=True)
            response = self.session.get(polling_url)
            if response.status_code != 200:
                raise Exception("Could not get results")
            if response.text == "":
                time.sleep(1)
                continue
            else:
                break

        # Use regex to search for src=""
        image_links = regex.findall(r'src="([^"]+)"', response.text)
        # Remove size limit
        normal_image_links = [link.split("?w=")[0] for link in image_links]
        # Remove duplicates
        return list(set(normal_image_links))

    def save_images(self, links: list, output_dir: str) -> None:
        """
        Saves images to output directory
        """
        # print("\n>[*] Downloading images...", end="\r")
        try:
            os.makedirs(output_dir)
        except FileExistsError:
            pass
        image_num = 0
        try:
            for link in links:
                with self.session.get(link, stream=True) as response:
                    # save response to file
                    response.raise_for_status()
                    with open(f"{output_dir}/{image_num}.jpg", "wb") as output_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            output_file.write(chunk)

                image_num += 1
        except requests.exceptions.MissingSchema as url_exception:
            raise Exception(
                "Inappropriate contents found in the generated images. Please try again or try another prompt."
            ) from url_exception
