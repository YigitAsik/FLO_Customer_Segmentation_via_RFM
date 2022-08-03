import datetime as dt
import pandas as pd
import seaborn as sns
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

import os
os.getcwd()

flo_data = pd.read_csv("flo_data.csv")
df = flo_data.copy()

df.head(10)

df.columns

df.describe().T
df.isnull().sum()
df.info()

df["total_num_orders"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["total_deposit"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]
df[["total_num_orders", "total_deposit"]].head()
df.iloc[0, :]

df[[col for col in df.columns if "date" in col]].info()
date_columns_names = [col for col in df.columns if "date" in col]

for j in date_columns_names:
    df[j] = pd.to_datetime(df[j])

#  Distributions
df.groupby("order_channel").agg({"master_id": "count",
                                 "total_num_orders": "sum",
                                 "total_deposit": "sum"})


df.sort_values(by="total_deposit", ascending=False)



df.sort_values(by="total_num_orders", ascending=False)

def preprocessing_for_rfm(data):
    data["total_num_orders"] = data["order_num_total_ever_online"] + data["order_num_total_ever_offline"]
    data["total_deposit"] = data["customer_value_total_ever_online"] + data["customer_value_total_ever_offline"]

    for i in [col for col in data.columns if "date" in col]:
        df[i] = pd.to_datetime(df[j])


##  RFM Metriklerinin Hesaplanması  ##

df["last_order_date"].max()
today_date = dt.datetime(2021, 6, 1)

df.groupby("master_id").agg({"total_num_orders": "sum",
                             "total_deposit": "sum"})
df[df["master_id"] == "00016786-2f5a-11ea-bb80-000d3a38a36f"]

rfm = df.groupby('master_id').agg({'last_order_date': lambda last_date: (today_date - last_date.max()).days,
                                     'total_num_orders': "sum",
                                     'total_deposit': "sum"})

rfm.columns = ["recency", "frequency", "monetary"]

rfm.head()

##  RFM Skorlarının Hesaplanması  ##

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.head()

##  RFM Segmentation  ##

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_lose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm_interested_v2 = rfm[(rfm["segment"] == "champions") | (rfm["segment"] == "loyal_customers")]
df_v2 = df[df["interested_in_categories_12"].str.contains("KADIN")]

rfm_interested_v2.merge(df_v2, on="master_id")

len(rfm_interested_v2)

rfm_interested_v2.head()
