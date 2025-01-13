import streamlit as st
import openai
import pandas as pd

# ✅ Securely Access the API Key Using Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# Global Variables
data = None
sentiment_summary_df = pd.DataFrame()
theme_summary_text = ""
all_comments_summary_text = ""

# ✅ GPT-4 Turbo Sentiment Analysis Function
def analyze_sentiment_gpt(comment):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert sentiment analyzer. Only return 'Positive', 'Negative', or 'Neutral'."},
                {"role": "user", "content": f"Analyze the sentiment of this comment: {comment}"}
            ],
            temperature=0
        )
        sentiment = response['choices'][0]['message']['content'].strip()
        return sentiment
    except Exception as e:
        return f"Error: {str(e)}"

# ✅ GPT-4 Turbo Summarization Function
def summarize_text_gpt(comments):
    try:
        combined_text = " ".join(comments[:5000])
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for summarizing comments."},
                {"role": "user", "content": f"Summarize the following comments: {combined_text}"}
            ],
            temperature=0
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except Exception as e:
        return f"Error: {str(e)}"

# ✅ Streamlit UI Setup
st.title("GPT-4 Turbo Sentiment & Summarization Web App")

# ✅ Upload CSV File
uploaded_file = st.file_uploader("Upload a CSV file with comments", type=["csv"])
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.success(f"CSV loaded with {len(data)} rows!")
    st.write(data.head())

# ✅ Theme and Keyword Inputs
theme = st.text_input("Enter Theme for Analysis")
keywords = st.text_area("Enter Keywords (comma-separated)").split(",")

# ✅ Perform Keyword Search
if st.button("Keyword Search"):
    if data is not None:
        data['Theme_Match'] = data['Comment'].apply(lambda x: any(kw.lower() in str(x).lower() for kw in keywords))
        theme_count = data['Theme_Match'].sum()
        st.success(f"The theme '{theme}' was found in {theme_count} comments.")
    else:
        st.error("Please upload a CSV file first.")

# ✅ Theme Sentiment Analysis
if st.button("Theme Sentiment Analysis"):
    if data is not None and 'Theme_Match' in data.columns:
        theme_comments = data[data['Theme_Match']]['Comment'].tolist()
        sentiments = [analyze_sentiment_gpt(comment) for comment in theme_comments]
        data.loc[data['Theme_Match'], 'Theme_Sentiment'] = sentiments
        sentiment_counts = pd.Series(sentiments).value_counts()
        st.success("Theme Sentiment Analysis Completed!")
        st.write("### Sentiment Breakdown")
        st.write(sentiment_counts)
    else:
        st.error("Please run the keyword search first!")

# ✅ Theme Summarization
if st.button("Theme Summarization"):
    if data is not None and 'Theme_Match' in data.columns:
        theme_comments = data[data['Theme_Match']]['Comment'].tolist()
        theme_summary_text = summarize_text_gpt(theme_comments)
        st.success("Theme Summarization Completed!")
        st.write("### Theme Summary:")
        st.write(theme_summary_text)
    else:
        st.error("Please run the keyword search first!")

# ✅ Sentiment Analysis for All Comments
if st.button("All Comments Sentiment Analysis"):
    if data is not None:
        sentiments = [analyze_sentiment_gpt(comment) for comment in data['Comment'].tolist()]
        data['Sentiment'] = sentiments
        sentiment_counts = pd.Series(sentiments).value_counts()
        st.success("Sentiment Analysis for All Comments Completed!")
        st.write("### Sentiment Breakdown:")
        st.write(sentiment_counts)
    else:
        st.error("Please upload a CSV file first!")

# ✅ Summarize All Comments
if st.button("All Comments Summarization"):
    if data is not None:
        all_comments_summary_text = summarize_text_gpt(data['Comment'].tolist())
        st.success("All Comments Summarization Completed!")
        st.write("### All Comments Summary:")
        st.write(all_comments_summary_text)
    else:
        st.error("Please upload a CSV file first!")

# ✅ Export Results
if st.button("Export Results"):
    if data is not None:
        export_path = "exported_results.xlsx"
        with pd.ExcelWriter(export_path) as writer:
            data.to_excel(writer, sheet_name="Comments", index=False)
            st.success(f"Results exported successfully to {export_path}")
    else:
        st.error("Please upload a CSV first!")
