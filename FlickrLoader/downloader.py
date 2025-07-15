import requests
import logging
import re

# ---------------------------------------------------------------------------- #
#                                  Downloader                                  #
# ---------------------------------------------------------------------------- #
class Downloader:
	def __init__(self, base_url: str = "https://www.flickr.com") -> None:
		self.base_url = base_url
		self.__api_key = None

	def __get_api_key(self, album_id: str) -> str:
		res = requests.get(f'{self.base_url}/photos/ethglobal/albums/{album_id}/')
		return re.search(r'(root\.YUI_config\.flickr\.api\.site_key = ")(.*?)(";)', res.text).group(2)
	
	def album_info(self, album_id: int):
		if not self.__api_key:
			self.__api_key = self.__get_api_key(album_id)
		baseparams = {
			"photoset_id": album_id,
			"nojsoncallback": 1,
			"api_key": self.__api_key,
			"hermesClient": 1,
			"format": "json",
			"hermes": 1
		}
		res = requests.get('https://api.flickr.com/services/rest', params={
			"method": "flickr.photosets.getInfo",
			**baseparams
		})
		album_title = dict(res.json()).get("photoset", {}).get("title", {}).get("_content", "")
		total_images = dict(res.json()).get("photoset", {}).get("count_photos", 0)
		return album_title, total_images

	def download_image(self, album_id: int):
		if not self.__api_key:
			self.__api_key = self.__get_api_key(album_id)
		baseparams = {
			"photoset_id": album_id,
			"nojsoncallback": 1,
			"api_key": self.__api_key,
			"hermesClient": 1,
			"format": "json",
			"hermes": 1
		}
		page = 1
		while True:
			res = requests.get('https://api.flickr.com/services/rest', params={
				"method": "flickr.photosets.getPhotos",
				"extras": "url_o",
				"per_page": 50,
				**baseparams,
				"page": page
			})
			if page > dict(res.json()).get("photoset", {}).get("pages", 0):
				break
			photos = dict(res.json()).get("photoset", {}).get("photo", [])
			for photo in photos:
				res = requests.get(photo["url_o"], stream=True)
				yield res.content, f"{photo['title']}.{res.headers['Content-Type'].split('/')[1]}"
			page += 1
