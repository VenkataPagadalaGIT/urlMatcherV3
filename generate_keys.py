import pickle
from pathlib import Path
import streamlit_authenticator as stauth

names = ["Sarak", "Eswar", "Admin", "Impressive USA", "Impressive AU"]
usernames = ["sarakdahal", "eswar", "admin", "ImpressiveUSA", "ImpressiveAU"]
passwords = ["#sarak@9861", "#venkata@9861", "#venkata@2262", "ImpressiveUSA", "ImpressiveAU"]

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
