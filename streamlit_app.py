import streamlit as st
import pandas as pd
from git import Repo
import os

# Configuration
REPO_OWNER = "awambaugh"  # Replace with your github username
REPO_NAME = "automate-venmo-requests"  # Replace with your repo name
CSV_FILE_PATH = "usernames.csv"  # Replace with the path to your csv
REPO_URL = f"https://{st.secrets['github_token']}@github.com/{REPO_OWNER}/{REPO_NAME}.git"
LOCAL_REPO_PATH = "./local_repo"  # Local path to clone the repo
SAVE_BUTTON_KEY = "save_button"
ADD_ROW_BUTTON_KEY = "add_row_button"
DATA_EDITOR_KEY = "data_editor"


def clone_or_pull_repo():
    """Clones or pulls the Git repository."""
    if os.path.exists(LOCAL_REPO_PATH):
        repo = Repo(LOCAL_REPO_PATH)
        repo.remotes.origin.pull()
    else:
        repo = Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)
    return Repo(LOCAL_REPO_PATH)


def load_csv_from_repo(repo):
    """Loads the CSV from the local repository."""
    try:
        csv_path = os.path.join(LOCAL_REPO_PATH, CSV_FILE_PATH)
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        st.error(f"CSV file not found at: {CSV_FILE_PATH}")
        return None
    except pd.errors.ParserError as e:
        st.error(f"Error parsing CSV: {e}")
        return None


def save_dataframe_to_repo(repo, df):
    """Saves the DataFrame back to the CSV and commits/pushes."""
    try:
        csv_path = os.path.join(LOCAL_REPO_PATH, CSV_FILE_PATH)
        df.to_csv(csv_path, index=False)
        repo.git.add(CSV_FILE_PATH)
        repo.git.commit("-m", "Update CSV from Streamlit app")
        origin = repo.remote(name="origin")
        origin.push()
        st.success("CSV updated and pushed to repository.")
    except Exception as e:
        st.error(f"Error saving and pushing: {e}")


def handle_save_button(repo, edited_df):
    if st.button("Save Changes", key=SAVE_BUTTON_KEY):
        save_dataframe_to_repo(repo, edited_df)
        st.session_state.edited_df = edited_df.copy()


def main():
    st.title("Relay Users (Be Careful)")

    repo = clone_or_pull_repo()
    df = load_csv_from_repo(repo)

    if df is not None:
        if "edited_df" not in st.session_state:
            st.session_state.edited_df = df.copy()

        edited_df = st.session_state.edited_df
        edited_df = st.data_editor(
            edited_df, key=DATA_EDITOR_KEY, num_rows="dynamic", hide_index=True)

        handle_save_button(repo, edited_df)


if __name__ == "__main__":
    main()
