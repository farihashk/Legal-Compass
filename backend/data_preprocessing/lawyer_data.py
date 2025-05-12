import pandas as pd

data = pd.read_csv("../data/lawyers_geocoded.csv", encoding="utf-8")
wills_lawyers = data[data["category"] == "Wills, Trusts & Estates"]

wills_lawyers.to_csv("../data/wills_lawyers.csv", index = False, encoding = "utf-8")