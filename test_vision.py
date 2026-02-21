from google.cloud import vision
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "vision_key.json"
)

client = vision.ImageAnnotatorClient(credentials=credentials)

print("Vision API connected successfully!")