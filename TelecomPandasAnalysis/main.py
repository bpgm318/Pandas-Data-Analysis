import pandas as pd
import matplotlib.pyplot as plt


# Creating list with names of 2 datasets. 1 dataset is mobile data usage in megabytes or "mb" and the other is mobile
# voice usage in minutes. Both are for the period of Apr 2025 to Mar 2026 and contain roughly 2800 users
datasets = ["mb", "minutes"]

# Using dictionary comprehension to create a dictionary of dataframes
dfs = {name: pd.read_csv(f"{name}.csv") for name in datasets}

# Cleaning Data
# Replacing invoice numbers with months they represent and type of data
# Replacing unnamed column header with new header for users
# Filling blank entries with 0
for name, df in dfs.items():
    df.rename(columns={"2991603593": f"May-25 ({name})",
                       "3005992431": f"Jun-25 ({name})",
                       "3019858340": f"Jul-25 ({name})",
                       "3037885950": f"Aug-25 ({name})",
                       "3051482952": f"Sep-25 ({name})",
                       "3073819737": f"Oct-25 ({name})",
                       "3088209048": f"Nov-25 ({name})",
                       "3102831898": f"Dec-25 ({name})",
                       "3117565686": f"Jan-26 ({name})",
                       "3132275148": f"Feb-26 ({name})",
                       "3146908306": f"Mar-26 ({name})",
                       },
              inplace=True)

    df.rename(columns={'Unnamed: 0': 'USER'}, inplace=True)

    df.fillna(0, inplace=True)

# Adding 12 month average column to both datasets rounded to nearest whole number
for name, df in dfs.items():
    df[f"12 Month Average ({name})"] = df.mean(axis=1, numeric_only=True).round(0).astype(int)

#Creating new dataframe with the month, the top user for that month, and the amount of data used that month
#Printing dataframe
highest_monthly_user_mb = dfs["mb"].loc[dfs["mb"].idxmax(), "USER"][1:13].tolist()

highest_monthly_amount_mb = (
    dfs["mb"].drop(columns=["12 Month Average (mb)"]).select_dtypes(include="number").max().tolist())

month_mb = dfs["mb"].drop(columns=["USER", "12 Month Average (mb)"]).columns.tolist()

top_monthly_users_mb = pd.DataFrame({"Month": month_mb,
                                  "USER": highest_monthly_user_mb,
                                  "Amount": highest_monthly_amount_mb})
print(top_monthly_users_mb)

#Plotting the standard deviation over the 12 month period for both voice usage and data usage
mb_std = dfs["mb"].drop(columns=["USER", "12 Month Average (mb)" ]).std().tolist()

min_std = dfs["minutes"].drop(columns=["USER", "12 Month Average (minutes)" ]).std().tolist()

std_months = pd.date_range(start='2025-04-01', periods=12, freq='MS')

formatted_std_months = std_months.strftime('%b %Y').tolist()

all_std = pd.DataFrame({"Month": formatted_std_months,
                                  "Data usage std": mb_std,
                                  "Voice usage std": min_std})
all_std.index = formatted_std_months
all_std.plot(kind="bar", title = "Standard deviation of voice and data usage")
plt.show()

#Printing top 10 users for each dataframe based on standard deviation
row_mb_std = dfs["mb"].drop(columns=["12 Month Average (mb)"])
row_mb_std["User std"] = row_mb_std.std(numeric_only=True, axis=1)
print(row_mb_std.sort_values(by="User std",ascending=False).head(10))

row_min_std = dfs["minutes"].drop(columns=["12 Month Average (minutes)"])
row_min_std["User std"] = row_min_std.std(numeric_only=True, axis=1)
print(row_min_std.sort_values(by="User std",ascending=False).head(10))

#Creating new dataframe with each user, their total data usage over 12 months,
#and the proportion that usage was of  total
prop_mb = dfs["mb"].drop(columns=["12 Month Average (mb)"])
prop_mb["Total"] = prop_mb.sum(axis=1, numeric_only=True)
prop_mb["Proportion"] = prop_mb["Total"].apply(lambda x: (x/prop_mb["Total"].sum())*100)

print(prop_mb[["USER", "Total", "Proportion"]].sort_values(by="Proportion", ascending=False).head(20))

#Creating new dataframe with each user, their total voice usage over 12 months,
#and the proportion that usage was of  total
prop_min = dfs["minutes"].drop(columns=["12 Month Average (minutes)"])
prop_min["Total"] = prop_min.sum(axis=1, numeric_only=True)
prop_min["Proportion"] = prop_min["Total"].apply(lambda x: (x/prop_min["Total"].sum())*100)

print(prop_min[["USER", "Total", "Proportion"]].sort_values(by="Proportion", ascending=False).head(20))

#Creating new dataframe with the month, the top user for that month, and the amount of minutes used that month
#Printing dataframe
highest_monthly_user_min = dfs["minutes"].loc[dfs["minutes"].idxmax(), "USER"][1:13].tolist()

highest_monthly_amount_min = (
    dfs["minutes"].drop(columns=["12 Month Average (minutes)"]).select_dtypes(include="number").max().tolist())

month_min = dfs["minutes"].drop(columns=["USER", "12 Month Average (minutes)"]).columns.tolist()

top_monthly_users_min = pd.DataFrame({"Month": month_min,
                                  "USER": highest_monthly_user_min,
                                  "Amount": highest_monthly_amount_min})
print(top_monthly_users_min)

# Creating new dataframe which is the combination of both datasets joined on the USER column
combined_dfs = dfs["mb"].merge(dfs["minutes"], how="inner", on="USER")

#Creating new dataframe with the 12 month averages for mobile data and mobile voice usage for each user
combined_dfs_averages = combined_dfs[["USER","12 Month Average (mb)", "12 Month Average (minutes)"]].copy()

#Creating new dataframe sorted by 12 month average (mb) in descending order. Printing top 10
combined_dfs_averages_mb = combined_dfs_averages.sort_values(by="12 Month Average (mb)", ascending=False)
print(combined_dfs_averages_mb.head(10))

#Creating new dataframe sorted by 12 month average (minutes) in descending order. Printing top 10
combined_dfs_averages_minutes = combined_dfs_averages.sort_values(by="12 Month Average (minutes)", ascending=False)
print(combined_dfs_averages_minutes.head(10))

#Creating new dataframe without 12 month averages
combined_dfs_no_averages  = combined_dfs.drop(columns=["12 Month Average (mb)", "12 Month Average (minutes)"])

# #Creating new dataframe with month totals
combined_dfs_no_averages_col_totals = combined_dfs_no_averages.drop(columns=["USER"]).sum()

#Plotting totals by month (mobile data)
combined_dfs_no_averages_col_totals.iloc[0:12].plot(kind="bar", title="Total in megabytes by month")
plt.show()

#Plotting totals by month (mobile voice)
combined_dfs_no_averages_col_totals.iloc[12:24].plot(kind="bar", title="Total in minutes by month")
plt.show()

#Plotting totals by month for both types of data side by side (megabytes and minutes)
combined_dfs_no_averages_col_totals.plot(kind="bar", title="Total by month")
plt.show()

#Querying to find all users with a 12 month average over 50 gigabytes. Printing result
print(combined_dfs_averages_mb.query("`12 Month Average (mb)` > 51200"))

#Querying to find all users with a 12 month average over 2000 minutes. Printing result
print(combined_dfs_averages_minutes.query("`12 Month Average (minutes)` > 2000"))

# Adding 2 columns to each dataframe for the row maximum as well as which month the maximum occurred
for name, df in dfs.items():
    df[f"12 Month Max ({name})"] = df.max(axis=1, numeric_only=True)
    df["Highest Month"] = df.idxmax(axis=1, numeric_only=True)

#Plotting highest data usage months across all users
dfs["mb"]["Highest Month"].value_counts().plot(kind="bar", title = "Highest data usage months")
plt.show()

#Plotting highest voice usage months across all users
dfs["minutes"]["Highest Month"].value_counts().plot(kind="bar", title = "Highest voice usage months")
plt.show()

#Plotting the data usage of the max user for each month
dfs["mb"].drop(columns=["12 Month Average (mb)"]).select_dtypes(include="number").max().plot(kind="bar",
                        title = "Max data usage for each month" )
plt.show()

#Plotting the voice usage of the max user for each month
dfs["minutes"].drop(columns=["12 Month Average (minutes)"]).select_dtypes(include="number").max().plot(kind="bar",
                        title = "Max voice usage for each month" )
plt.show()

#Plotting the average data usage per user for each month
usage_by_user_mb = (
        (dfs["mb"].drop(columns=["12 Month Average (mb)", "12 Month Max (mb)"]).sum(numeric_only=True))/len(dfs["mb"]))

usage_by_user_mb.plot(kind="bar", title = "Average data usage per user (mb)")
plt.show()

#Plotting the average voice usage per user for each month
usage_by_user_min = (
        (dfs["minutes"].drop(columns=[
            "12 Month Average (minutes)", "12 Month Max (minutes)"]).sum(numeric_only=True))/len(dfs["minutes"]))
usage_by_user_min.plot(kind="bar", title = "Average voice usage per user (minutes)")
plt.show()

#Using a lambda function to classify users in a new column as "high", "medium" or "low" usage users based on the
# 12 month average. This is applied for both dataframes and counts of each type printed
dfs["mb"]["Type"] = dfs["mb"]["12 Month Average (mb)"].apply(lambda x: "High Usage" if x > 30000 else
                                                ("Medium Usage" if x > 3000
                                                 else "Low Usage"))
print(dfs["mb"]["Type"].value_counts())

dfs["minutes"]["Type"] = dfs["minutes"]["12 Month Average (minutes)"].apply(lambda x: "High Usage" if x > 1600 else
                                                ("Medium Usage" if x > 500
                                                 else "Low Usage"))
print(dfs["minutes"]["Type"].value_counts())

# Plotting the above value counts for type for both dataframes
dfs["mb"]["Type"].value_counts().plot(kind="pie", title="Usage type (mb)")
plt.show()

dfs["minutes"]["Type"].value_counts().plot(kind="pie", title="Usage type (min)")
plt.show()

#Exporting takeaway metrics in a new dataframe (csv) for both data and voice
takeaway_dataframe_mb = dfs["mb"][["USER","12 Month Average (mb)","12 Month Max (mb)","Highest Month"]].copy()
takeaway_dataframe_mb.to_csv("Takeaway (mb)",index=False)

takeaway_dataframe_min = (
                dfs["minutes"][["USER","12 Month Average (minutes)","12 Month Max (minutes)","Highest Month"]].copy())
takeaway_dataframe_min.to_csv("Takeaway (minutes)",index=False)