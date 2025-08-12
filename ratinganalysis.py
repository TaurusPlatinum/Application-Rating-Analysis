import pandas as pd

applications = pd.read_csv("applications.csv", low_memory=False)
industries = pd.read_csv("industries.csv", low_memory=False)
applications = applications.drop_duplicates(subset=['applicant_id'], keep='first').reset_index(drop=True)
applications['External Rating'] = pd.to_numeric(applications['External Rating'], errors='coerce').fillna(0)
applications['Education level'] = applications['Education level'].fillna("Secondary")
applications['Applied at'] = pd.to_datetime(applications['Applied at'], errors='coerce')
applications['Age'] = pd.to_numeric(applications['Age'], errors='coerce')
applications['Amount'] = pd.to_numeric(applications['Amount'], errors='coerce')
applications['is_married'] = applications['Marital status'].str.lower().str.contains('married')
applications['is_kyiv'] = applications['Location'].str.lower().str.contains('êè¿â|kiev|kyiv')
industries['Industry'] = industries['Industry'].str.strip()
applications['Industry'] = applications['Industry'].str.strip()
applications = applications.merge(industries, on='Industry', how='left')
applications['weekday'] = applications['Applied at'].dt.weekday 
applications['is_weekday'] = applications['weekday'] < 5

age_score = ((applications['Age'] >= 35) & (applications['Age'] <= 55)).astype(int) * 20
weekday_score = applications['is_weekday'].fillna(False).astype(int) * 20
married_score = applications['is_married'].fillna(False).astype(int) * 20
kyiv_score = applications['is_kyiv'].fillna(False).astype(int) * 10
industry_score = applications['Score'].fillna(0).clip(0, 20)

external_rating = applications['External Rating']
external_high_score = (external_rating >= 7).astype(int) * 20
external_low_score = (external_rating <= 2).astype(int) * (-20)

applications['raw_rating'] = (
    age_score +
    weekday_score +
    married_score +
    kyiv_score +
    industry_score +
    external_high_score +
    external_low_score
)

applications.loc[applications['Amount'].isna() | (external_rating == 0), 'raw_rating'] = 0
applications['rating'] = applications['raw_rating'].clip(lower=0, upper=100).astype(int)
accepted = applications[applications['rating'] > 0].copy()


weekly_avg = (
    accepted
    .set_index('Applied at')
    .resample('W-MON')['rating']
    .mean()
    .reset_index()
    .rename(columns={'Applied at': 'week_starting_monday', 'rating': 'avg_rating'})
)
weekly_avg['avg_rating'] = weekly_avg['avg_rating'].fillna(0)

print("Number of accepted applications:", len(accepted))
print("\nAverage rating by week:")
print(weekly_avg)


accepted.to_csv("accepted_applications.csv", index=False)
weekly_avg.to_csv("weekly_avg_rating.csv", index=False)
