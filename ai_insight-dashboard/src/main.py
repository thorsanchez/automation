import pandas as pd
from fetch_api import fetch_comments
from fetch_csv import fetch_csv_feedback
from clean_text import clean_text
from ai_summary import summarize_feedback

def main():
    api_df = fetch_comments(limit=20)
    csv_df = fetch_csv_feedback()

    api_df = api_df.rename(columns={"body": "text"})
    csv_df = csv_df.rename(columns={"feedback": "text"})
    #sameina data
    combined_df = pd.concat([api_df, csv_df], ignore_index=True)
    #clean text
    combined_df["clean_text"] = combined_df["text"].apply(clean_text)

    #senda allt inn i gemini
    report = summarize_feedback(combined_df["clean_text"].tolist())

    with open("output/report.md", "w") as f:
        f.write(report)

if __name__ == "__main__":
    main()
