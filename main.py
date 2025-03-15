import streamlit as st
from datetime import date
import numpy as np
import json

# Streamlit UI Configuration
st.set_page_config(page_title="Personal Library Manager",
                   page_icon="📚", layout="wide")

# Custom Styling
st.markdown("""
    <style>
        #MainMenu, footer {visibility: hidden;}
        .main-title { font-size: 36px; font-weight: bold; color: #2E86C1; text-align: center; }
        .subtitle { font-size: 18px; color: #555; text-align: center; }
        .stButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# Page Header
st.markdown("""
    <h1 class="main-title">📚 Personal Library Manager</h1>
    <p class="subtitle">By Hamza Sheikh</p>
    """, unsafe_allow_html=True)

# Initialize Book Storage
if "books" not in st.session_state:
    st.session_state.books = []

# Sidebar Navigation
st.sidebar.title("📖 Library Navigation")
page = st.sidebar.radio("Go to:", [
                        "📚 Add Book", "📂 View Library", "🔍 Search Book", "📊 Library Statistics"])

# 📌 Add Book
if page == "📚 Add Book":
    st.subheader("📖 Add a New Book")

    # Form Layout
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Book Title")
        author = st.text_input("Author Name")
    with col2:
        publication_year = st.number_input(
            "Publication Year", min_value=1000, max_value=2100, step=1, value=date.today().year)
        genre = st.selectbox("Genre", ["Fiction", "Non-fiction", "Mystery", "Romance",
                                       "Fantasy", "Science Fiction", "Horror", "History", "Other"])

    read_status = st.radio("Reading Status", [
                           "Not Read", "Currently Reading", "Finished"], horizontal=True)

    if st.button("📥 Add Book"):
        if title and author:
            st.session_state.books.append({
                "title": title,
                "author": author,
                "year": publication_year,
                "genre": genre,
                "status": read_status
            })
            st.success(f"✅ '{title}' by {author} added successfully!")
        else:
            st.error("❌ Please enter both the title and the author's name.")

# 📌 View Library
elif page == "📂 View Library":
    st.subheader("📚 Your Book Collection")
    if not st.session_state.books:
        st.info("No books added yet. Start adding some!")
    else:
        for index, book in enumerate(st.session_state.books):
            with st.expander(f"📖 {book['title']} by {book['author']} ({book['year']})"):
                st.write(f"**Genre:** {book['genre']}")
                st.write(f"**Reading Status:** {book['status']}")

                # Popover for Delete Confirmation
                with st.popover(f"❌ Remove '{book['title']}'"):
                    st.write("Are you sure you want to delete this book?")
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("⚠️ Confirm Delete", key=f"confirm_{index}"):
                            st.session_state.books.pop(index)
                            st.rerun()
                    with col2:
                        if st.button("Cancel", key=f"cancel_{index}"):
                            st.write("Deletion cancelled.")

# 📌 Search Book
elif page == "🔍 Search Book":
    st.subheader("🔍 Search for a Book")
    search_query = st.text_input("Enter a book title or author name")

    if st.button("Search"):
        if search_query:
            results = [book for book in st.session_state.books if search_query.lower(
            ) in book['title'].lower() or search_query.lower() in book['author'].lower()]
            if results:
                for book in results:
                    st.write(
                        f"📖 **{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} | *{book['status']}*")
            else:
                st.warning("No matching books found.")
        else:
            st.error("Please enter a search query.")

# 📌 Library Statistics
elif page == "📊 Library Statistics":
    st.subheader("📊 Library Statistics")

    # Using NumPy for efficient calculations
    total_books = len(st.session_state.books)
    read_books = np.sum(
        [book["status"] == "Finished" for book in st.session_state.books])
    read_percentage = np.round(
        (read_books / total_books) * 100, 2) if total_books > 0 else 0

    # Styled Metrics Display
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="📚 Total Books", value=total_books)
    with col2:
        st.metric(label="📖 Books Read", value=read_books)
    with col3:
        st.metric(label="📊 Percentage Read", value=f"{read_percentage}%")

    # Progress bar visualization
    st.markdown("<h4 style='margin-top: 20px;'>📈 Reading Progress</h4>",
                unsafe_allow_html=True)
    st.progress(read_percentage / 100)

    # Display dynamic message based on reading progress
    if read_percentage == 0:
        st.warning("📌 You haven't read any books yet! Start reading today!")
    elif read_percentage < 50:
        st.info("📖 Keep going! You're making progress.")
    elif read_percentage < 100:
        st.success("🚀 You're doing great! Almost there.")
    else:
        st.balloons()
        st.success("🎉 Congratulations! You've read all your books!")

    # 📥 Export Library to JSON
    st.markdown("<h4 style='margin-top: 30px;'>📤 Export Library</h4>",
                unsafe_allow_html=True)

    if total_books > 0:
        # Convert books to JSON format
        library_json = json.dumps(st.session_state.books, indent=4)
        st.download_button(label="📂 Download Library as JSON",
                           data=library_json,
                           file_name="books.json",
                           mime="application/json")
    else:
        st.info("📌 No books to export yet.")
