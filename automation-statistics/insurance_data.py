import pandas as pd

insurance_csv = "insurance.csv"
df = pd.read_csv(insurance_csv)

#print(df.head())
#print(df.describe())
#age,sex,bmi,children,smoker,region,charges

def univariate(df):
    output_df = pd.DataFrame(columns=['type', 'count', 'missing', 'unique'])
    for col in df:
        dtype = df[col].dtype
        count = df[col].count()
        missing = df[col].isna().sum()
        unique = df[col].nunique()
        print(dtype, count, missing, unique)
print(univariate(df))