from alive_progress import alive_bar
import requests
import argparse
import re
import os

from downloader import Downloader

# ---------------------------------------------------------------------------- #
#                                   ArgParser                                  #
# ---------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description='FlickrLoader')
parser.add_argument('url', type=str, help='URL of the Flickr album')
parser.add_argument('outputpath', type=str, default=None, help='Output folder')
parser.add_argument('--reference', type=str, default=None, help='Folder containing reference images')
parser.add_argument('--match', type=float, default=0.6, help='Face matching threshold')
args = parser.parse_args()

# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #
if not "albums" in args.url:
	res = requests.get(args.url)
	args.url = res.url
album_id = re.search(r'(?:albums|sets)/([\d]+)(?:/)?', args.url).group(1)

downloader = Downloader()
if args.reference:
	from matcher import FaceMatcher
	facematcher = FaceMatcher(args.match, args.reference)
else:
	facematcher = None
album_title, total_images = downloader.album_info(album_id)
if not args.outputpath:
	args.outputpath = album_title
os.makedirs(args.outputpath, exist_ok=True)
with alive_bar(total_images, title=album_title) as bar:
	for img in downloader.download_image(album_id):
		if (facematcher and facematcher.match(img[0])) or not facematcher:
			with open(f"{args.outputpath}/{img[1]}", "wb") as f:
				f.write(img[0])
		bar()
