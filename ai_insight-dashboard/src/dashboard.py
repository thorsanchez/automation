import streamlit as st
import pandas as pd

from fetch_api import fetch_comments
from fetch_csv import fetch_csv_feedback
from clean_text import clean_text
from ai_summary import summarize_feedback


def load_data():
    #fetch og sameina feedback fra API og CSV
    #breyta col i text
    api_df = fetch_comments(limit=20).rename(columns={"body": "text"})
    csv_df = fetch_csv_feedback().rename(columns={"feedback": "text"})

    combined_df = pd.concat([api_df, csv_df], ignore_index=True)
    combined_df["clean_text"] = combined_df["text"].apply(clean_text)

    return combined_df


def main():
    st.set_page_config(
        page_title="Insights Dashboard",
        layout="wide"
    )

    st.title("Customer Insights")
    st.write(
        "The dashboard analyzes customer feedback from csv and json file "
        "using py and llm"
    )

    #load data
    with st.spinner("Loading and processing data"):
        df = load_data()

    # Metrics
    col1, col2 = st.columns(2)
    col1.metric("Total feedback items", len(df))
    col2.metric("Data Sources", "API + CSV")

    st.divider()

    # Raw data
    st.subheader("raw customer feedback")
    st.dataframe(df[["text"]], use_container_width=True)

    st.divider()

    #Summary
    st.subheader("Gemini generated insights")

    if st.button("Generate AI Summary"):
        with st.spinner("Analyzing feedback with AI..."):
            report = summarize_feedback(df["clean_text"].tolist())

        st.markdown(report)

    st.divider()


if __name__ == "__main__":
    main()
