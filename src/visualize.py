import json

import altair as alt
import pandas as pd

with open("data/result.json", "rb") as fh:
    result = json.load(fh)

df = pd.DataFrame(result).T
df = df.reset_index().rename(columns={"index": "location"})

# Plot total time
alt.Chart(df).mark_bar().encode(y="location", x="total time").save(
    "data/viz/total_time.html"
)

# Plot time per month per type of travel
alt.Chart(df.drop("total time", axis=1).melt(id_vars="location")).mark_bar().encode(
    y="location", x="sum(value)", color="variable"
).save("data/viz/monthly_split.html")
