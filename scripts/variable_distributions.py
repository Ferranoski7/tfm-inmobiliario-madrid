from db import engine
import pandas as pd
from sqlalchemy import text
import matplotlib.pyplot as plt
import os
import seaborn as sns


variables = [
"ASSETID",
"PERIOD",
"PRICE",
"UNITPRICE",
"CONSTRUCTEDAREA",
"ROOMNUMBER",
"BATHNUMBER",
"HASLIFT",
"HASAIRCONDITIONING",
"HASPARKINGSPACE",
"ISPARKINGSPACEINCLUDEDINPRICE",
"PARKINGSPACEPRICE",
"ISDUPLEX",
"ISSTUDIO",
"ISINTOPFLOOR",
"FLOORCLEAN",
"FLATLOCATIONID",
"BUILTTYPEID_1",
"BUILTTYPEID_2",
"BUILTTYPEID_3",
"DISTANCE_TO_CITY_CENTER",
"DISTANCE_TO_METRO" ,
"DISTANCE_TO_CASTELLANA",
"LATITUDE",
"LONGITUDE",
"HASTERRACE",
"HASBOXROOM",
"HASWARDROBE",
"HASDOORMAN",
"HASGARDEN",
"HASNORTHORIENTATION",
"HASSOUTHORIENTATION",
"HASEASTORIENTATION",
"HASWESTORIENTATION",
"CADCONSTRUCTIONYEAR",
"CADMAXBUILDINGFLOOR",
"CADDWELLINGCOUNT",
"HASSWIMMINGPOOL",
]


def get_dataset():
    """
    Load the given columns from the database and return a pandas dataframe with all the obseervations.
    """
    query = """
        SELECT *
        FROM madrid_sale;"""
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    return df
    
if __name__ == "__main__":
    df = get_dataset()
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # For each column, check if it is numeric al or categorical and plot the distribution
    for column in df.columns:
        if df[column].dtype in ['int64', 'float64']:
            print(f"{column} is numeric")
            plt.figure(figsize=(8, 5))
            sns.histplot(df[column].dropna(), bins=50, kde=True, color='skyblue')
            plt.title(f"Distribution of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.tight_layout()
            plt.savefig(os.path.join(plots_dir, f"{column}_hist.png"))
            plt.clf()  # Clear figure for next plot
        else:
            print(f"{column} is categorical")
            value_counts = df[column].value_counts()
            print(value_counts)
            # Barplot for categorical variables with not too many categories
            if value_counts.shape[0] <= 30:
                plt.figure(figsize=(10, 5))
                sns.barplot(x=value_counts.index.astype(str), y=value_counts.values, palette="viridis")
                plt.title(f"Value Counts of {column}")
                plt.xlabel(column)
                plt.ylabel("Count")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig(os.path.join(plots_dir, f"{column}_barplot.png"))
                plt.clf()
            value_counts.to_csv(os.path.join(plots_dir, f"{column}_value_counts.txt"), sep='\t')