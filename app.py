import streamlit as st
import requests
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# -------------------- LOAD TOKEN --------------------
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {}
if GITHUB_TOKEN:
    HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


st.title("GitHub Profile Analyzer")

username = st.text_input("Enter GitHub Username")


# -------------------- CACHE HELPERS --------------------
@st.cache_data(ttl=3600)
def get_github_user(username):
    url = f"https://api.github.com/users/{username}"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else None


@st.cache_data(ttl=3600)
def get_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else []


@st.cache_data(ttl=3600)
def get_languages(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/languages"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else {}


# -------------------- GLOBAL LANGS --------------------
def get_all_languages(username, repos):
    all_langs = {}

    for repo in repos:
        lang_data = get_languages(username, repo["name"])

        for lang, value in lang_data.items():
            all_langs[lang] = all_langs.get(lang, 0) + value

    return all_langs


# -------------------- MAIN APP --------------------
if username:

    user_data = get_github_user(username)

    if user_data:

        # ---------------- PROFILE ----------------
        st.image(user_data["avatar_url"], width=150)
        st.subheader(user_data.get("name", "No Name"))
        st.write(user_data.get("bio", "No bio available"))

        col1, col2, col3 = st.columns(3)
        col1.metric("Followers", user_data["followers"])
        col2.metric("Following", user_data["following"])
        col3.metric("Public Repos", user_data["public_repos"])

        # ---------------- REPOS ----------------
        st.markdown("### Repositories")

        repos = get_repos(username)

        
        # ---------------- GLOBAL LANGS ----------------
        st.markdown("## Overall Language Usage")

        all_langs = get_all_languages(username, repos)

        if all_langs:
            fig, ax = plt.subplots()

            ax.bar(all_langs.keys(), all_langs.values())

            ax.set_title("Total Language Distribution (All Repos)")
            ax.set_xlabel("Languages")
            ax.set_ylabel("Bytes of Code")

            plt.xticks(rotation=45, ha="right")

            st.pyplot(fig)
            st.write("---")

        for repo in repos:
            st.write(f"**{repo['name']}** Star: {repo['stargazers_count']}")
            st.write(repo["html_url"])

            lang_data = get_languages(username, repo["name"])

            if lang_data:
                fig, ax = plt.subplots(figsize=(3, 3))
                ax.pie(
                    list(lang_data.values()),
                    labels=list(lang_data.keys()),
                    autopct='%1.1f%%'
                )
                ax.set_title(repo["name"])

                st.pyplot(fig)

            st.write("---")


    else:
        st.error("User not found")