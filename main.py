import streamlit as st
from polyfuzz import PolyFuzz
import pandas as pd
from polyfuzz.models import TFIDF
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
from PIL import Image

# USER AUTH
names = ["Sarak", "Eswar", "Admin", "Impressive USA", "Impressive AU"]
usernames = ["sarakdahal", "eswar", "admin", "ImpressiveUSA", "ImpressiveAU"]
# Load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
                                    "urlMatcher", "#12#2262", cookie_expiry_days=7)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect.")
if authentication_status == None:
    st.warning("Please enter your username and password.")
if authentication_status:
    image = Image.open('impressive.jpg')
    st.image(image)

    st.subheader(f"Welcome {name}")
    st.subheader('Python URL / Redirect Mapping Tool with Default Value')
    st.subheader('Directions:')
    st.write('- Upload complete crawl \n - Upload a list of 404s in.CSV format (URL column named URL) \n - Would not '
             'recommend with over 10k URLs (very slow) ')

    st.write("Author - [Venkata Pagadala](https://www.linkedin.com/in/venkata-pagadala/)")
    # Importing the URL CSV files
    url = st.text_input('The URL to Match', placeholder='Enter domain (www.google.com)')
    file1 = st.file_uploader("Upload 404 CSV File")
    file2 = st.file_uploader("Upload Crawl CSV File")
    if file1 is not None and file2 is not None:
        broken = pd.read_csv(file1)
        current = pd.read_csv(file2)
        ROOTDOMAIN = url
        # Converting DF to List
        broken_list = broken["URL"].tolist()
        broken_list = [sub.replace(ROOTDOMAIN, '') for sub in broken_list]
        current_list = current["Address"].tolist()
        current_list = [sub.replace(ROOTDOMAIN, '') for sub in current_list]

        for i in range(2, 3):
            tfidf = TFIDF(n_gram_range=(i, i))
            model = PolyFuzz(tfidf)
            model.match(broken_list, current_list)
            df1 = model.get_matches()
            # Polishing and Pruning
            df1["Similarity"] = df1["Similarity"].round(3)
            index_names = df1.loc[df1['Similarity'] < .10].index
            amt_dropped = len(index_names)
            df1.drop(index_names, inplace=True)
            df1["To"] = ROOTDOMAIN + df1["To"]
            df1["From"] = ROOTDOMAIN + df1["From"]
            df = pd.DataFrame()
            df['To'] = current['Address']
            df['Title'] = current['Title 1']
            df['Meta Description'] = current['Meta Description 1']
            df['H1'] = current['H1-1']
            val = df[df['To'].str.contains(ROOTDOMAIN)]
            mainTitle = val['Title'][0]
            mainMeta = val['Meta Description'][0]
            mainH1 = val['H1'][0]
            df3 = pd.merge(df, df1, on='To')
            df3 = df3[['Similarity', 'From', 'To', 'Title', 'Meta Description', 'H1']]
            var = .45
            df3.loc[df3["Similarity"] < var, "To"] = ROOTDOMAIN
            df3.loc[df3["Similarity"] < var, "Title"] = mainTitle
            df3.loc[df3["Similarity"] < var, "Meta Description"] = mainMeta
            df3.loc[df3["Similarity"] < var, "H1"] = mainH1
            # df3 = df3.sort_values(by='Similarity', ascending=False)
            df3


        # Downloading of File
        @st.cache
        def convert_df(df3):
            return df3.to_csv().encode('utf-8')


        csv = convert_df(df3)
        st.download_button("Download Output", csv, "file.csv", "text/csv", key='download-csv')

        authenticator.logout("Logout", "main")
