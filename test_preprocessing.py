from core.data_loader import load_agriculture_data
from core.data_processor import preprocess_data

df = load_agriculture_data()

cleaned_df, report = preprocess_data(df)

print("Original shape:", df.shape)
print("Cleaned shape:", cleaned_df.shape)
print("\nData Quality Report:")
print(report)

print("\nCleaned columns:")
print(cleaned_df.columns.tolist())