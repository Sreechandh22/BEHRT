import pandas as pd
import os
from datetime import datetime, timedelta

print("🚀 Script started...")

file_path = "C:/Users/sreec/OneDrive/Desktop/Clinical/clinical_extracted_data.xlsx"
df = pd.read_excel(file_path)

# ✅ If 'Patient_ID' is missing, create it using MRN or row index
if "Patient_ID" not in df.columns:
    df["Patient_ID"] = df["mrn"] if "mrn" in df.columns else range(1, len(df) + 1)
    print("✅ Generated Patient_ID from MRN.")

print("✅ File loaded successfully.")

# 🚀 **Step 1: Generate 'Visit_Date' Based on Chief Complaint (if missing)**
if "Visit_Date" not in df.columns:
    df["Visit_Date"] = pd.to_datetime(datetime.today().date())  # Assign today’s date if missing
    print("✅ Assigned default Visit_Date.")

# ✅ Convert Visit_Date to datetime
df["Visit_Date"] = pd.to_datetime(df["Visit_Date"], errors="coerce")
print("✅ Dates converted to datetime.")

# ✅ Sort data by Patient_ID and Visit_Date
df = df.sort_values(by=["Patient_ID", "Visit_Date"])
print("✅ Data sorted.")

# 🚀 **Step 2: Fixed Interval Approach**
fixed_intervals = []
interval_days = [30, 60, 15]  # Modify as needed

for interval in interval_days:
    temp_df = df.copy()
    temp_df["Fixed_Interval_Date"] = temp_df.groupby("Patient_ID")["Visit_Date"].transform(
        lambda x: [x.min() + timedelta(days=i * interval) for i in range(len(x))]
    )
    temp_df["Interval_Days"] = interval
    fixed_intervals.append(temp_df)

df_fixed = pd.concat(fixed_intervals, ignore_index=True)
print(f"✅ Fixed intervals processed. Rows: {len(df_fixed)}")

# 🚀 **Step 3: Real Visit Intervals + Zero-Padding**
real_visit_intervals = []

for patient_id, group in df.groupby("Patient_ID"):
    group = group.sort_values("Visit_Date")
    visits = list(group["Visit_Date"].dropna())

    if not visits:
        continue

    real_intervals = [visits[0]]
    for i in range(1, len(visits)):
        gap = (visits[i] - visits[i-1]).days
        real_intervals.append(visits[i])

        if gap > 90:
            zero_pad_date = visits[i-1] + timedelta(days=90)
            real_intervals.insert(-1, zero_pad_date)

    group["Real_Visit_Intervals"] = real_intervals
    real_visit_intervals.append(group)

df_real = pd.concat(real_visit_intervals, ignore_index=True)
print(f"✅ Real intervals processed. Rows: {len(df_real)}")

# 🚀 **Step 4: Save Results**
output_path_fixed = "C:/Users/sreec/OneDrive/Desktop/Clinical/visit_timestamps_fixed.xlsx"
output_path_real = "C:/Users/sreec/OneDrive/Desktop/Clinical/visit_timestamps_real.xlsx"

if not df_fixed.empty:
    df_fixed.to_excel(output_path_fixed, index=False)
    print(f"✅ Fixed Interval Dataset saved: {output_path_fixed}")
else:
    print("❌ No data in Fixed Interval dataset!")

if not df_real.empty:
    df_real.to_excel(output_path_real, index=False)
    print(f"✅ Real Visit Interval Dataset saved: {output_path_real}")
else:
    print("❌ No data in Real Visit Interval dataset!")

print("🎉 Script completed!")
