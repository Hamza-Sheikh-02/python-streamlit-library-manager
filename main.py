import streamlit as st
from datetime import date
import numpy as np
import json
from dotenv import load_dotenv
import os
import psycopg2

# --- Database Connection Setup ---
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    st.error("DATABASE_URL is not set in the .env file")
    st.stop()

try:
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
except psycopg2.Error as e:
    st.error(f"Error connecting to the database: {e}")
    st.stop()

# Create the "books" table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER NOT NULL,
        genre TEXT NOT NULL,
        status TEXT NOT NULL
    );
""")
conn.commit()

# --- Streamlit UI Configuration & Styling ---
st.set_page_config(page_title="Personal Library Manager",
                   page_icon="📚", layout="wide")
st.markdown("""
    <style>
        #MainMenu, footer {visibility: hidden;}
        .main-title { font-size: 36px; font-weight: bold; color: #2E86C1; text-align: center; }
        .subtitle { font-size: 18px; color: #555; text-align: center; }
        .stButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)
st.markdown("""
    <h1 class="main-title">📚 Personal Library Manager</h1>
    <p class="subtitle">By Hamza Sheikh</p>
    """, unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("📖 Library Navigation")
page = st.sidebar.radio("Go to:", [
                        "📚 Add Book", "📂 View Library", "🔍 Search Book", "📊 Library Statistics"])

# --- Add Book Section ---
if page == "📚 Add Book":
    st.subheader("📖 Add a New Book")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Book Title")
        author = st.text_input("Author Name")
    with col2:
        publication_year = st.number_input(
            "Publication Year", min_value=1000, max_value=2100, step=1, value=date.today().year)
        genre = st.selectbox("Genre", ["Fiction", "Non-fiction", "Mystery",
                             "Romance", "Fantasy", "Science Fiction", "Horror", "History", "Other"])
    read_status = st.radio("Reading Status", [
                           "Not Read", "Currently Reading", "Finished"], horizontal=True)

    if st.button("📥 Add Book"):
        if title and author:
            try:
                cursor.execute(
                    "INSERT INTO books (title, author, year, genre, status) VALUES (%s, %s, %s, %s, %s)",
                    (title, author, publication_year, genre, read_status)
                )
                conn.commit()
                st.success(f"✅ '{title}' by {author} added successfully!")
            except psycopg2.Error as e:
                st.error(f"❌ Error adding book: {e}")
        else:
            st.error("❌ Please enter both the title and the author's name.")

# --- View Library Section ---
elif page == "📂 View Library":
    st.subheader("📚 Your Book Collection")
    try:
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        if not books:
            st.info("No books added yet. Start adding some!")
        else:
            for book in books:
                book_id, title, author, year, genre, status = book
                with st.expander(f"📖 {title} by {author} ({year})"):
                    st.write(f"**Genre:** {genre}")
                    st.write(f"**Reading Status:** {status}")
                    if st.button(f"Remove {title}", key=f"remove_{book_id}"):
                        try:
                            cursor.execute(
                                "DELETE FROM books WHERE id = %s", (book_id,))
                            conn.commit()
                            st.success(f"✅ '{title}' removed successfully!")
                        except psycopg2.Error as e:
                            st.error(f"❌ Error removing book: {e}")
    except psycopg2.Error as e:
        st.error(f"❌ Error fetching books: {e}")

# --- Search Book Section ---
elif page == "🔍 Search Book":
    st.subheader("🔍 Search for a Book")
    search_query = st.text_input("Enter a book title or author name")
    if st.button("Search"):
        if search_query:
            try:
                query = "SELECT * FROM books WHERE title ILIKE %s OR author ILIKE %s"
                cursor.execute(
                    query, (f"%{search_query}%", f"%{search_query}%"))
                results = cursor.fetchall()
                if results:
                    for book in results:
                        book_id, title, author, year, genre, status = book
                        st.write(
                            f"📖 **{title}** by {author} ({year}) - {genre} | *{status}*")
                else:
                    st.warning("No matching books found.")
            except psycopg2.Error as e:
                st.error(f"❌ Error searching for books: {e}")
        else:
            st.error("Please enter a search query.")

# --- Library Statistics Section ---
elif page == "📊 Library Statistics":
    st.subheader("📊 Library Statistics")
    try:
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books_result = cursor.fetchone()
        total_books = total_books_result[0] if total_books_result else 0
        cursor.execute("SELECT COUNT(*) FROM books WHERE status = 'Finished'")
        read_books_result = cursor.fetchone()
        read_books = read_books_result[0] if read_books_result else 0
        read_percentage = np.round(
            (read_books / total_books) * 100, 2) if total_books > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="📚 Total Books", value=total_books)
        with col2:
            st.metric(label="📖 Books Read", value=read_books)
        with col3:
            st.metric(label="📊 Percentage Read", value=f"{read_percentage}%")

        st.markdown(
            "<h4 style='margin-top: 20px;'>📈 Reading Progress</h4>", unsafe_allow_html=True)
        st.progress(read_percentage / 100)

        if read_percentage == 0:
            st.warning("📌 You haven't read any books yet! Start reading today!")
        elif read_percentage < 50:
            st.info("📖 Keep going! You're making progress.")
        elif read_percentage < 100:
            st.success("🚀 You're doing great! Almost there.")
        else:
            st.balloons()
            st.success("🎉 Congratulations! You've read all your books!")

        st.markdown(
            "<h4 style='margin-top: 30px;'>📤 Export Library</h4>", unsafe_allow_html=True)
        if total_books > 0:
            cursor.execute("SELECT * FROM books")
            books = cursor.fetchall()
            library_json = json.dumps(books, indent=4)
            st.download_button(label="📂 Download Library as JSON",
                               data=library_json,
                               file_name="books.json",
                               mime="application/json")
        else:
            st.info("📌 No books to export yet.")
    except psycopg2.Error as e:
        st.error(f"❌ Error calculating statistics: {e}")
