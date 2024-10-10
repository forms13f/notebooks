import pandas as pd
import numpy as np
from IPython.display import display_html
from datetime import date
from typing import List
import report


class QuarterlyReportsCollection:
    def __init__(self, cik, from_year, to_year):
        self.cik = cik
        self.from_year = from_year
        self.to_year = to_year
        self.reports = {}
        self._generate_quarters()
        self._get_reports()

    def _generate_quarters(self):
        """
        Generate a list of quarters in the format YYYY-Q<d> where d=1..4, stopping at the current quarter.
        """
        current_year = date.today().year
        current_month = date.today().month
        current_quarter = (current_month - 1) // 3 + 1

        self.quarters = []
        for year in range(self.from_year, self.to_year + 1):
            for qtr in range(1, 5):
                if year == current_year and qtr > current_quarter:
                    break
                self.quarters.append(f"{year}-Q{qtr}")

    def _get_reports(self):
        """
        Call QuarterReport() for each quarter and populate the reports map with key as quarter and value as report.
        """
        for quarter in self.quarters:
            quarter_report = report.QuarterReport(quarter, self.cik)
            if quarter_report.header is not None:
                self.reports[quarter] = quarter_report

    def display_reports(self, by="value", output="native"):
        """
        This method converts the reports into an array sorted by quarter ascending and populates data for display.

        Args:
            by (str): Determines whether to display by 'shares', 'value', or 'fraction'. Default is 'value'.
            output (str): Determines whether to display as 'as_html' or 'native'. Default is 'native'.

        Raises:
            ValueError: If the 'by' parameter is not one of 'shares', 'value', or 'fraction'.
            ValueError: If the 'output' parameter is not one of 'as_html' or 'native'.
        """

        if len(self.reports) == 0:
            print("No reports available.")
            return

        # Validate the 'by' parameter
        if by not in ["shares", "value", "fraction"]:
            raise ValueError("Invalid 'by' parameter. Use 'shares', 'value', or 'fraction'.")

        # Validate the 'output' parameter
        if output not in ["as_html", "native"]:
            raise ValueError("Invalid 'output' parameter. Use 'as_html' or 'native'.")

        # List to hold all report data
        data = []

        # Sort reports by quarter in ascending order
        sorted_reports = [self.reports[quarter] for quarter in sorted(self.reports.keys())]

        # Loop through each QuarterReport to collect data
        for report in sorted_reports:
            for holding in report.holdings:
                header = report.header
                data.append({
                    'cik': header.cik,
                    'company_name': header.company_name,
                    'period_of_report': header.period_of_report,
                    'report_quarter': header.report_quarter,
                    'name_of_issuer': holding.name_of_issuer,
                    'title_of_class': holding.title_of_class,
                    'cusip': holding.cusip,
                    'ticker': holding.ticker,
                    'value': holding.value,
                    'ssh_prnamt': holding.ssh_prnamt,
                    'ssh_prnamt_type': holding.ssh_prnamt_type,
                })

        # Create a DataFrame from the data
        df = pd.DataFrame(data)

        # Calculate total value and add percentage column
        df['value'] = df['value']/1000
        value_total = df['value'].sum()
        df['%'] = ((df['value'] / value_total) * 100).round(2)

        # Determine the column to pivot by
        pivot_column = 'value' if by == 'value' else 'ssh_prnamt' if by == 'shares' else '%'

        # Pivot the DataFrame to get the desired structure
        pivot_df = df.pivot_table(
            index=['name_of_issuer', 'ticker'],
            columns='report_quarter',
            values=pivot_column,
            aggfunc='first'  # Use 'first' in case there are duplicate entries
        )

        # Sort the columns so that report_quarters are in chronological order
        pivot_df = pivot_df.sort_index(axis=1)

        # Replace NaN with 0
        pivot_df = pivot_df.fillna(0).reset_index()

        # Set display format based on the 'by' parameter
        # Rename columns
        pivot_df.rename(columns={'name_of_issuer': 'Name', 'ticker': 'Symbol'}, inplace=True)

        # Ensure 'Name' and 'Symbol' are the leftmost columns
        quarter_columns = [col for col in pivot_df.columns if col not in ['Name', 'Symbol']]
        overall_columns = ['Name', 'Symbol'] + quarter_columns
        pivot_df = pivot_df[overall_columns]

        first_quarter = quarter_columns[0]
        pivot_df = pivot_df.sort_values(by=first_quarter, ascending=False)

        # Remove the name attribute from the columns
        pivot_df.columns.name = None

        # Remove the index name from the DataFrame
        pivot_df.index.name = None

        # Get the latest quarter's report
        latest_quarter = sorted(self.reports.keys())[-1]
        latest_report = self.reports[latest_quarter]

        # Extract the company name and convert it to uppercase
        company_name_upper = latest_report.header.company_name.upper()

        # Set the title using the uppercase company name
        if by == 'value':
            title = f"Value in thousands $ Over Quarters Held by {company_name_upper}"
        elif by == 'shares':
            title = f"Number of Shares Over Quarters Held by {company_name_upper}"
        else:
            title = f"Percentage Over Quarters Held by {company_name_upper}"

        if output == "as_html":
            if by == 'fraction':
                pd.options.display.float_format = '{:,.2f}'.format
            elif by == 'value':
                pd.options.display.float_format = '${:,.0f}'.format
            else:
                pd.options.display.float_format = '{:,.0f}'.format
            display_html(f"<h3>{title}</h3>" + pivot_df.to_html(index=False), raw=True)
        else:
            if by == 'fraction':
                pd.options.display.float_format = '{:.2f}'.format
            elif by == 'value':
                pd.options.display.float_format = '{:.0f}'.format
            else:
                pd.options.display.float_format = '{:.0f}'.format
            display(pivot_df)
        pd.reset_option('display.float_format')
