import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FILE_NAME = "orders.csv"


def load_and_clean_orders(filename):
  """Load orders.csv, skip non-numeric or negative amounts with warnings,
    and return a clean DataFrame."""
  try:
    df = pd.read_csv(filename)
  except FileNotFoundError:
    print(f"Error: '{filename}' not found. Please place it in the same folder.")
    sys.exit(1)

  # Clean text columns gently
  df["Month"] = df["Month"].astype(str).str.strip()
  df["Category"] = df["Category"].astype(str).str.strip()

  # Convert Amount to numeric; invalid text like 'N/A' becomes NaN
  numeric_amount = pd.to_numeric(df["Amount"], errors="coerce")

  valid_rows = []
  for idx, raw_amt in enumerate(numeric_amount):
    order_id = df.loc[idx, "OrderID"] if "OrderID" in df.columns else idx + 1

    if pd.isna(raw_amt):
      print(f"Warning: Row {order_id} skipped - Amount must be a number.")
    elif raw_amt < 0:
      print(f"Warning: Row {order_id} skipped - Amount cannot be negative.")
    else:
      row_copy = df.loc[idx].copy()
      row_copy["Amount"] = float(raw_amt)
      valid_rows.append(row_copy)

  if not valid_rows:
    print("No valid orders found to analyse.")
    sys.exit(1)

  clean_df = pd.DataFrame(valid_rows).reset_index(drop=True)
  print(f"Valid orders analysed: {len(clean_df)}\n")
  return clean_df


def show_monthly_spending(df, show_chart=True):
  """Display monthly totals, overall total, and the best month."""
  # Preserve order of appearance in the data
  month_order = list(dict.fromkeys(df["Month"]))
  monthly = (
      df.groupby("Month", sort=False)["Amount"]
      .sum()
      .reindex(month_order)
  )

  total_spending = float(np.sum(monthly.values))
  best_month = monthly.idxmax()
  best_amount = float(monthly.max())

  for month, amt in monthly.items():
    print(f"{month} : Rs. {amt:g}")
  print(f"Total: Rs. {total_spending:g}")
  print(f"Best month: {best_month} (Rs. {best_amount:g})")

  if show_chart:
    plt.figure(figsize=(7, 4))
    plt.bar(monthly.index, monthly.values)
    plt.title("Monthly Spending")
    plt.xlabel("Month")
    plt.ylabel("Amount (Rs.)")
    plt.tight_layout()
    plt.show()


def show_category_and_stats(df, show_chart=True):
  """Display category percentage share and order statistics using NumPy."""
  amounts = df["Amount"].to_numpy(dtype=float)
  total = float(np.sum(amounts))

  cat_totals = (
      df.groupby("Category", sort=False)["Amount"]
      .sum()
      .sort_values(ascending=False)
  )

  for category, amt in cat_totals.items():
    pct = (float(amt) / total) * 100 if total > 0 else 0.0
    print(f"{category} : Rs. {float(amt):g} ({pct:.2f}%)")

  mean_val = float(np.mean(amounts))
  median_val = float(np.median(amounts))
  print(f"Mean order value: Rs. {mean_val:.2f}")
  print(f"Median order value: Rs. {median_val:.2f}")

  if show_chart:
    plt.figure(figsize=(6, 6))
    plt.pie(
        cat_totals.values,
        labels=cat_totals.index,
        autopct="%1.2f%%",
        startangle=140,
    )
    plt.title("Category Spending Share")
    plt.tight_layout()
    plt.show()


def show_order_statistics(df):
  """Display order count, mean, median, and best month."""
  amounts = df["Amount"].to_numpy(dtype=float)
  monthly = df.groupby("Month", sort=False)["Amount"].sum()
  best_month = monthly.idxmax()
  best_amount = float(monthly.max())

  print(f"Orders analysed: {len(df)}")
  print(f"Mean order value: Rs. {float(np.mean(amounts)):.2f}")
  print(f"Median order value: Rs. {float(np.median(amounts)):.2f}")
  print(f"Best month: {best_month} (Rs. {best_amount:g})")


def main():
  df = load_and_clean_orders(FILE_NAME)

  print("Select an option:")
  print("1. Monthly spending")
  print("2. Order statistics")
  print("3. Category share and statistics")
  choice = input("Enter choice (1/2/3): ").strip()

  print()
  if choice == "1":
    show_monthly_spending(df, show_chart=True)
  elif choice == "2":
    show_order_statistics(df)
  elif choice == "3":
    show_category_and_stats(df, show_chart=True)
  else:
    print("Invalid choice. Please run again and enter 1, 2, or 3.")


if __name__ == "__main__":
  main()