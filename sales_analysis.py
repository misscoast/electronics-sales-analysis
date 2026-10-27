"""Electronics sales analysis with the csv module, verified with pandas."""

import csv
import math
import re
import sys

import pandas as pd

CSV_PATH ="data\electronics_sales.csv"
THRESHOLD = 50_000


# 1. Read the data ----------------------------------------------------------
def read_sales(path):
    """Read the CSV into a list of dicts and report what was found."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames
    print(f"Rows read: {len(rows)}")
    print(f"Columns: {', '.join(columns)}")
    return rows


# 2. Convert numeric data ---------------------------------------------------
def parse_number(value):
    """Return value as a float, repairing only formatting problems.

    Repaired: surrounding spaces, a leading 'KES' label, thousands commas.
    Not repaired (raises ValueError): blanks, 'N/A', number words, and
    anything else that is not a plain number once the formatting is removed.
    """
    if value is None:
        raise ValueError("missing value")
    text = value.strip()
    if text == "":
        raise ValueError("blank value")
    text = re.sub(r"^KES\s*", "", text, flags=re.IGNORECASE)
    # commas are only accepted as proper thousands separators: 38,999
    if "," in text:
        if not re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?", text):
            raise ValueError(f"misplaced thousands separator: {value!r}")
        text = text.replace(",", "")
    if not re.fullmatch(r"\d+(\.\d+)?", text):
        raise ValueError(f"not a number: {value!r}")
    return float(text)


def convert_rows(rows):
    """Return (clean_rows, skipped_rows).

    Each skipped entry is {'row', 'sale_id', 'reason'}; each clean row gets
    an int quantity, a float unit price, its revenue, and a 'repairs' list.
    """
    clean, skipped = [], []
    for line_no, row in enumerate(rows, start=2):  # line 1 is the header
        sale_id = row.get("sale_id", "?")
        try:
            try:
                qty = parse_number(row["quantity"])
            except ValueError as exc:
                raise ValueError(f"quantity: {exc}")
            try:
                price = parse_number(row["unit_price_kes"])
            except ValueError as exc:
                raise ValueError(f"unit_price_kes: {exc}")
            if qty != int(qty) or qty <= 0:
                raise ValueError(f"quantity: must be a positive whole number, got {row['quantity']!r}")
            if price <= 0:
                raise ValueError(f"unit_price_kes: must be positive, got {row['unit_price_kes']!r}")
        except ValueError as exc:
            skipped.append({"row": line_no, "sale_id": sale_id, "reason": str(exc)})
            continue

        repairs = []
        for field in ("quantity", "unit_price_kes"):
            if row[field] != row[field].strip() or not re.fullmatch(r"\d+(\.\d+)?", row[field]):
                repairs.append(f"{field} {row[field]!r} -> {parse_number(row[field]):g}")
        new = dict(row)
        new["quantity"] = int(qty)
        new["unit_price_kes"] = price
        new["revenue"] = new["quantity"] * new["unit_price_kes"]
        new["repairs"] = repairs
        clean.append(new)
    return clean, skipped


# 3. Total revenue ----------------------------------------------------------
def total_revenue(rows):
    total = 0.0
    for r in rows:
        total += r["quantity"] * r["unit_price_kes"]
    return total


def kes(amount):
    return f"KES {amount:,.2f}"


# 4. Revenue by field (plain dict) -----------------------------------------
def revenue_by(rows, field):
    totals = {}
    for r in rows:
        key = r[field]
        if key in totals:
            totals[key] += r["quantity"] * r["unit_price_kes"]
        else:
            totals[key] = r["quantity"] * r["unit_price_kes"]
    return totals


# 5. Top N ------------------------------------------------------------------
def top_n(totals, n):
    """Highest revenue first; ties are broken alphabetically by name."""
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:n]


# 6. High-value transactions ------------------------------------------------
def high_value(rows, threshold):
    return [r for r in rows if r["quantity"] * r["unit_price_kes"] >= threshold]


# 7. Statistics -------------------------------------------------------------
def mean(values):
    if len(values) == 0:
        raise ValueError("mean() needs at least one value; the list is empty")
    total = 0.0
    for v in values:
        total += v
    return total / len(values)


def median(values):
    if len(values) == 0:
        raise ValueError("median() needs at least one value; the list is empty")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def minimum_maximum(values):
    if len(values) == 0:
        raise ValueError("minimum_maximum() needs at least one value; the list is empty")
    low = high = values[0]
    for v in values[1:]:
        if v < low:
            low = v
        if v > high:
            high = v
    return low, high


# 8. Verify with pandas -----------------------------------------------------
def _clean_number_series(series):
    """Same rules as parse_number, applied column-wise."""
    s = series.fillna("").astype(str).str.strip()
    s = s.str.replace(r"^(?i:KES)\s*", "", regex=True)
    ok_commas = ~s.str.contains(",") | s.str.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?")
    s = s.where(ok_commas, "")
    s = s.str.replace(",", "", regex=False)
    s = s.where(s.str.fullmatch(r"\d+(\.\d+)?"), None)
    return pd.to_numeric(s, errors="coerce")


def verify_with_pandas(path, my_results):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["quantity"] = _clean_number_series(df["quantity"])
    df["unit_price_kes"] = _clean_number_series(df["unit_price_kes"])
    df = df.dropna(subset=["quantity", "unit_price_kes"])
    df = df[(df["quantity"] > 0) & (df["quantity"] == df["quantity"].round())
            & (df["unit_price_kes"] > 0)].copy()
    df["revenue"] = df["quantity"] * df["unit_price_kes"]

    def report(label, mine, theirs):
        if isinstance(mine, dict):
            same = (mine.keys() == theirs.keys()
                    and all(math.isclose(mine[k], theirs[k]) for k in mine))
        else:
            same = math.isclose(mine, theirs)
        print(f"  {label}: {'MATCH' if same else 'MISMATCH'}")
        return same

    print("\nPandas verification:")
    results = [
        report("clean row count", my_results["rows"], len(df)),
        report("total revenue", my_results["total"], df["revenue"].sum()),
        report("revenue by product", my_results["by_product"],
               df.groupby("product")["revenue"].sum().to_dict()),
        report("revenue by store", my_results["by_store"],
               df.groupby("store")["revenue"].sum().to_dict()),
        report("revenue by payment method", my_results["by_payment"],
               df.groupby("payment_method")["revenue"].sum().to_dict()),
        report("high-value sale count", my_results["high_value_count"],
               int((df["revenue"] >= THRESHOLD).sum())),
        report("mean revenue", my_results["mean"], df["revenue"].mean()),
        report("median revenue", my_results["median"], df["revenue"].median()),
        report("minimum revenue", my_results["min"], df["revenue"].min()),
        report("maximum revenue", my_results["max"], df["revenue"].max()),
    ]
    top_pd = (df.groupby("product")["revenue"].sum().reset_index()
              .sort_values(["revenue", "product"], ascending=[False, True])
              .head(3))
    top_pd = [(p, r) for p, r in zip(top_pd["product"], top_pd["revenue"])]
    same_top = ([p for p, _ in my_results["top3"]] == [p for p, _ in top_pd])
    print(f"  top 3 products: {'MATCH' if same_top else 'MISMATCH'}")
    results.append(same_top)
    return all(results)


def main(path=CSV_PATH):
    rows = read_sales(path)

    clean, skipped = convert_rows(rows)
    print(f"\nUsable rows: {len(clean)} | Skipped rows: {len(skipped)}")
    print("Skipped:")
    for s in skipped:
        print(f"  line {s['row']} ({s['sale_id']}): {s['reason']}")
    print("Repaired:")
    for r in clean:
        for note in r["repairs"]:
            print(f"  {r['sale_id']}: {note}")

    total = total_revenue(clean)
    print(f"\nTotal revenue: {kes(total)}")

    by_product = revenue_by(clean, "product")
    by_store = revenue_by(clean, "store")
    by_payment = revenue_by(clean, "payment_method")

    print("\nRevenue by product (highest first):")
    for product, revenue in sorted(by_product.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {product}: {kes(revenue)}")
    print("\nRevenue by store:")
    for store, revenue in sorted(by_store.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {store}: {kes(revenue)}")
    print("\nRevenue by payment method:")
    for method, revenue in sorted(by_payment.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {method}: {kes(revenue)}")

    top3 = top_n(by_product, 3)
    print("\nTop 3 products:")
    for rank, (product, revenue) in enumerate(top3, start=1):
        print(f"  {rank}. {product}: {kes(revenue)}")

    big = high_value(clean, THRESHOLD)
    print(f"\nSales of {kes(THRESHOLD)} or more: {len(big)}")
    for r in big:
        print(f"  {r['sale_id']} {r['sale_date']} {r['store']} - {r['product']} "
              f"x{r['quantity']}: {kes(r['revenue'])}")
    per_store = {store: sum(1 for r in big if r["store"] == store) for store in by_store}
    print("High-value sales per store:")
    for store, n in per_store.items():
        print(f"  {store}: {n}")

    revenues = [r["revenue"] for r in clean]
    low, high = minimum_maximum(revenues)
    avg, mid = mean(revenues), median(revenues)
    print("\nPer-transaction revenue:")
    print(f"  mean: {kes(avg)}\n  median: {kes(mid)}")
    print(f"  minimum: {kes(low)}\n  maximum: {kes(high)}")

    my_results = {
        "rows": len(clean), "total": total, "by_product": by_product,
        "by_store": by_store, "by_payment": by_payment, "top3": top3,
        "high_value_count": len(big), "mean": avg, "median": mid,
        "min": low, "max": high,
    }
    verify_with_pandas(path, my_results)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else CSV_PATH)