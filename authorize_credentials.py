
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

scopes = ['https://www.googleapis.com/auth/calendar']

flow = InstalledAppFlow.from_client_secrets_file("config/credentials.json", scopes=scopes)
credentials = flow.run_console()
pickle.dump(credentials, open("config/token.pkl", "wb"))