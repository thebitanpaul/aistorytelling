import streamlit as st
import openai
import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create SQLite table if not exists
conn = sqlite3.connect('stories.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS stories 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT)''')
conn.commit()
st.title("AI-Enhanced Interactive Storytelling")

# Search for a story
search_query = st.text_input("Search for a story by title")
search_button_clicked = st.button("Search")
if search_button_clicked:
    c.execute("SELECT * FROM stories WHERE title LIKE ?", ('%' + search_query + '%',))
    rows = c.fetchall()
    if rows:
        st.write("Matching Story:")
        for row in rows:
            st.write("Title: \n\n", row[1])
            st.write("Content: \n\n", row[2])
    else:
        st.write("No matching story found.")

# Delete a story
delete_button_clicked = st.button("Delete Story")
if delete_button_clicked:
    if not search_query:
        st.write("Please enter the title of the story you want to delete.")
    else:
        c.execute("SELECT * FROM stories WHERE title=?", (search_query,))
        row = c.fetchone()
        if row:
            c.execute("DELETE FROM stories WHERE title=?", (search_query,))
            conn.commit()
            st.write("Story deleted successfully.")
        else:
            st.write("No story found with the given title.")

# Basic story creation
new_story_title = st.text_input("Enter a story title")
initial_text = st.text_area("Start writing your story...", height=200)

if initial_text:
    if st.button("Save Your Story"):
        if not new_story_title:
            st.write("Please enter a title for the story.")
            st.stop()
        if not initial_text:
            st.write("Please write or generate the story first.")
            st.stop()

        # Save to SQLite database
        c.execute("INSERT INTO stories (title, content) VALUES (?, ?)", (new_story_title, initial_text))
        conn.commit()
        st.write("Story saved successfully.")

    # AI work here:
ai_text = st.text_area("Enter Your Prompt")

if st.button("Get AI suggestions"):
        response = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=ai_text,
            max_tokens=1000  # Increase max_tokens to get more text in response
        )
        generated_text = response.choices[0].text.strip()
        
        st.write("AI results that you can copy/paste in the text box: \n\n", generated_text)    

# Close SQLite connection
conn.close()
