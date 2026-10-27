Electronics Sales Analysis 📊
Project Overview

This project analyses electronics sales data using Python's built-in csv module. It calculates total revenue, compares product and store performance, identifies high-value transactions, and computes descriptive statistics.

Pandas is used to verify the results of the main analysis.

Objectives

The project demonstrates how to:

Read CSV files using csv.DictReader.
Convert numeric values and handle invalid data.
Calculate total sales revenue.
Group revenue by product, store, and payment method using dictionaries.
Rank the top three products by revenue.
Filter high-value transactions above KES 50,000.
Calculate mean, median, minimum, and maximum transaction revenue.
Verify the results using pandas.
Technologies Used
Python
CSV module
Pandas
Git and GitHub
Project Structure
text
SALES ANALYTICS/
├── data/
│   └── electronics_sales.csv
├── src/
│   └── sales_analytics/
│       └── __init__.py
├── sales_analysis.py
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
└── .gitignore

Data Cleaning Rules

The program applies the following rules when processing the dataset.

Numeric Conversion

The parse_number() function converts numeric strings into numbers.

The following formatting issues are repaired:

Leading and trailing whitespace is removed.
A leading KES currency label is removed.
Correctly formatted thousands separators are removed.

For example, KES 38,999 can be converted into a numeric value.

Invalid Values

The following values are rejected:

Missing values.
Empty strings.
Text that cannot be interpreted as a number.
Incorrectly formatted thousands separators.

Rows containing invalid quantities or unit prices are skipped, and the program records the row number, sale ID, and reason for skipping each row.

Quantity Validation

Quantity must be a positive whole number. Zero, negative, and fractional quantities are rejected because the analysis treats each record as a sale of a positive whole number of units.

Unit Price Validation

Unit price must be positive. Zero and negative prices are rejected under the project's cleaning rules.

Revenue Calculation

Revenue for each transaction is calculated using:

Revenue = Quantity × Unit Price

The total revenue is the sum of revenue across all valid transactions.

Amounts are displayed in Kenyan shillings (KES), with two decimal places and thousands separators.

Revenue Analysis

The program calculates revenue by:

Product.
Store.
Payment method.

Product revenue is sorted from highest to lowest.

The top three products are ranked by total revenue. If two products have the same revenue, their names are ordered alphabetically.

High-Value Transactions

A transaction qualifies as high-value when its revenue is strictly greater than KES 50,000.

The program displays qualifying transactions and counts how many high-value transactions occurred at each store.

Statistical Analysis

The program implements its own functions to calculate:

Mean: The average transaction revenue.
Median: The middle transaction revenue after sorting.
Minimum: The smallest transaction revenue.
Maximum: The largest transaction revenue.

Each statistical function raises a clear ValueError if called with an empty list.

The minimum and maximum are calculated using a loop rather than Python's built-in min() and max() functions.

Pandas Verification

Pandas independently recomputes the headline analysis after applying equivalent numeric cleaning and validation rules.

The verification checks:

Number of valid transactions.
Total revenue.
Revenue by product.
Revenue by store.
Revenue by payment method.
Number of high-value transactions.
Mean transaction revenue.
Median transaction revenue.
Minimum and maximum transaction revenue.
Top three products.

The program reports MATCH when the results agree and MISMATCH when they differ.

Because both implementations use equivalent cleaning rules, differences may indicate inconsistencies in data cleaning, filtering, grouping, ranking, or calculations.

How to Run
1. Install Dependencies

Ensure Python is installed.

Activate the project's virtual environment if necessary, then install pandas:

bash
python -m pip install pandas

2. Check the Dataset

Ensure the CSV file is located at:

data/electronics_sales.csv

The dataset should contain the columns required by the analysis, including quantity, unit_price_kes, product, store, and payment_method.

3. Run the Analysis

From the project root directory, execute:

bash
python sales_analysis.py


The program prints the analysis results and pandas verification status to the terminal.

Results

The actual results are generated when the program runs against the supplied dataset.

The output includes total revenue, product rankings, revenue breakdowns, high-value transactions, descriptive statistics, skipped-row reasons, and pandas verification results.

Conclusion

This project demonstrates practical Python data analysis using CSV processing, numeric validation, dictionaries, list comprehensions, sorting, and statistical calculations. Pandas provides an additional way to verify the headline results.

The analysis helps identify the highest-revenue products, compare store performance, understand payment-method revenue, and examine high-value transactions.