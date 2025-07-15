import face_recognition
from io import BytesIO
import logging
import os

# ---------------------------------------------------------------------------- #
#                                  FaceMatcher                                 #
# ---------------------------------------------------------------------------- #
class FaceMatcher:
	def __init__(self, match: float, references: str):
		self.__match = match
		self.__references = references
		self.__known_face_encodings = []
		for img in os.listdir(self.__references):
			image = face_recognition.load_image_file(f"{self.__references}/{img}")
			self.__known_face_encodings.append(face_recognition.face_encodings(image)[0])

	def match(self, image_bytes: bytes) -> bool:
		image_io = BytesIO(image_bytes)
		image = face_recognition.load_image_file(image_io)
		face_encodings = face_recognition.face_encodings(image)
		return True in [result for face_encoding in face_encodings for result in face_recognition.compare_faces(
			self.__known_face_encodings, face_encoding, 1.0 - self.__match
		)]
