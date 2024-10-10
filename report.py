from datetime import date
from typing import List, Optional
from form import *
import forms13f
import pandas as pd
import numpy as np
from IPython.display import display_html


class ReportHeader:
    """
    A class to represent the header information of a financial quarter report.

    Attributes:
        urls (list): List of URLs for the report documents.
        accession_numbers (list): List of accession numbers for the reports.
        submission_type (str): Type of submission.
        public_document_count (int): Count of public documents.
        period_of_report (str): Period of the report.
        report_quarter (str): Quarter of the report.
        filing_dates (list): List of filing dates.
        date_as_of_change (str): Date as of change.
        effectiveness_date (str): Effectiveness date.
        cik (str): Central Index Key (CIK) of the company.
        company_name (str): Name of the company.
        irs_number (str): IRS number of the company.
        state_of_incorporation (str): State of incorporation.
        fiscal_year_end (str): Fiscal year end.
        form_type (str): Type of form.
        sec_act (str): SEC act.
        business_address (str): Business address of the company.
        business_phone (str): Business phone number of the company.
        table_value_total (int): Total value in the table.
        table_entry_total (int): Total number of entries in the table.

    Methods:
        __init__(urls, accession_numbers, submission_type, public_document_count, period_of_report, report_quarter,
                 filing_dates, date_as_of_change, effectiveness_date, cik, company_name, irs_number,
                 state_of_incorporation, fiscal_year_end, form_type, sec_act, business_address, business_phone,
                 table_value_total, table_entry_total):
            Initializes the ReportHeader object with the provided attributes.

        display_as_html():
            Displays the header information as an HTML header.
    """

    def __init__(self, urls, accession_numbers, submission_type, public_document_count,
                 period_of_report, report_quarter, filing_dates, date_as_of_change,
                 effectiveness_date, cik, company_name, irs_number, state_of_incorporation,
                 fiscal_year_end, form_type, sec_act, business_address,
                 business_phone, table_value_total, table_entry_total):
        self.urls = urls
        self.accession_numbers = accession_numbers
        self.submission_type = submission_type
        self.public_document_count = public_document_count
        self.period_of_report = period_of_report
        self.report_quarter = report_quarter
        self.filing_dates = filing_dates
        self.date_as_of_change = date_as_of_change
        self.effectiveness_date = effectiveness_date
        self.cik = cik
        self.company_name = company_name
        self.irs_number = irs_number
        self.state_of_incorporation = state_of_incorporation
        self.fiscal_year_end = fiscal_year_end
        self.form_type = form_type
        self.sec_act = sec_act
        self.business_address = business_address
        self.business_phone = business_phone
        self.table_value_total = table_value_total
        self.table_entry_total = table_entry_total

    def display_as_html(self):
        """
        Display the header information of the quarter report as an HTML header.

        This method extracts relevant header information such as the quarter, company name, CIK, filing dates,
        accession numbers, holdings, and value, and formats it into an HTML header for display.

        Returns:
            None
        """
        """
        This method takes the header information of the quarter report and displays it as an HTML header.
        """
        # Extract header information
        quarter = self.report_quarter
        company_name = self.company_name
        cik = self.cik
        filing_dates = ', '.join([date.strftime('%Y-%m-%d') for date in self.filing_dates])
        accession_links = ', '.join(
            [f'<a href="{url}" target="_blank">{acc}</a>' for acc, url in zip(self.accession_numbers, self.urls)])
        holdings = self.table_entry_total
        value_k = self.table_value_total // 1000

        # Create HTML header
        header_html = f"""
            <h3>Quarter: {quarter}</h3>
            <p>Company Name: {company_name}<br>
            CIK: {cik}<br>
            Filing Dates: {filing_dates}<br>
            Accession Numbers: {accession_links}<br>
            Holdings: {holdings}<br>
            Value: ${value_k:,}k</p>
            """
        display_html(header_html, raw=True)


class QuarterReport:
    """
    A class to represent a financial quarter report and its associated holdings.

    Attributes:
        quarter (str): The quarter of the report in the format 'YYYY-Q<1-4>'.
        cik (str): Central Index Key (CIK) of the company.
        header (ReportHeader): The header information of the quarter report.
        holdings (list): A list of holdings associated with the quarter report.

    Methods:
        __init__(quarter, cik):
            Initializes the QuarterReport object with the provided quarter and CIK.

        _get_quarter_report():
            Retrieves and consolidates the quarter report data for the given CIK and quarter.

        display_header_as_html():
            Displays the header information of the quarter report as an HTML header.

        display_holdings_as_html():
            Displays the holdings of the quarter report as an HTML table.
    """
    def __init__(self, quarter, cik):
        self.quarter = quarter
        self.cik = cik
        self.header = None
        self.holdings = None
        self._get_quarter_report()

    def _get_quarter_report(self):
        # Convert the quarter to the period of form
        period_of_report = quarter_to_period_of_report(self.quarter)

        # Get the forms for the given CIK and period of form
        forms = get_forms_for_period(self.cik, period_of_report)
        if not forms:
            return

        # Aggregate the holdings from the forms
        self.holdings = consolidate_holdings(forms)

        # Create the header
        urls = [form.header.url for form in forms]
        accession_numbers = [form.header.accession_number for form in forms]
        filing_dates = [form.header.filed_as_of_date for form in forms]
        first_report = forms[0]

        self.header = ReportHeader(
            urls=urls,
            accession_numbers=accession_numbers,
            submission_type=first_report.header.submission_type,
            public_document_count=first_report.header.public_document_count,
            period_of_report=first_report.header.period_of_report,
            report_quarter=self.quarter,
            filing_dates=filing_dates,
            date_as_of_change=first_report.header.date_as_of_change,
            effectiveness_date=first_report.header.effectiveness_date,
            cik=first_report.header.cik,
            company_name=first_report.header.company_name,
            irs_number=first_report.header.irs_number,
            state_of_incorporation=first_report.header.state_of_incorporation,
            fiscal_year_end=first_report.header.fiscal_year_end,
            form_type=first_report.header.form_type,
            sec_act=first_report.header.sec_act,
            business_address=first_report.header.business_address,
            business_phone=first_report.header.business_phone,
            table_value_total=first_report.header.table_value_total,
            table_entry_total=first_report.header.table_entry_total,
        )

    def display_header_as_html(self):
        """
        This method calls the displayQuarterReportHeader method from the ReportHeader instance.
        """
        if self.header:
            self.header.display_as_html()

    def display_holdings(self, output="native"):
        """
        This method takes the list of holdings (ApiV1FormEntry objects) and displays them as an HTML table or native DataFrame.

        Args:
            output (str): Determines whether to display as 'as_html' or 'native'. Default is 'as_html'.

        Raises:
            ValueError: If the 'output' parameter is not one of 'as_html' or 'native'.
        """
        if output not in ["as_html", "native"]:
            raise ValueError("Invalid 'output' parameter. Use 'as_html' or 'native'.")

        if not self.holdings:
            return

        # Extract relevant fields from holdings
        holdings_data = [
            {
                'Name': holding.name_of_issuer,
                'Symbol': holding.ticker,
                'CUSIP': holding.cusip,
                'Value, $k': int(holding.value / 1000),  # Convert value to float and divide by 1000
                'Shares': holding.ssh_prnamt
            }
            for holding in self.holdings
        ]

        # Create DataFrame
        df_holdings = pd.DataFrame(holdings_data)

        # Calculate total value and add percentage column
        value_total = df_holdings['Value, $k'].sum()
        df_holdings['%'] = ((df_holdings['Value, $k'] / value_total) * 100).round(2)


        # Sort by Value in descending order
        df_holdings = df_holdings.sort_values(by='Value, $k', ascending=False)

        if output == "as_html":
            df_holdings_style = df_holdings.style.format({
                'Shares': '{:,}'.format,  # Format Shares with commas
                'Value, $k': '{:,.0f}'.format,  # Format Value with commas and no decimal points
                '%': '{:.2f}'.format  # Format Value with commas and no decimal points
            })
            df_holdings_html = df_holdings_style.to_html(index=False)
            display_html(df_holdings_html, raw=True)
        else:
            display(df_holdings)


def quarter_to_period_of_report(quarter):
    """
    Convert a quarter string to the corresponding period of report date.

    This function takes a quarter in the format 'YYYY-Q<1-4>' and converts it to the corresponding
    period of report end date in the format 'YYYY-MM-DD'.

    Args:
        quarter (str): The quarter string in the format 'YYYY-Q<1-4>'.

    Returns:
        str: The period of report end date in the format 'YYYY-MM-DD'.

    Raises:
        ValueError: If the quarter format is invalid.
    """
    year, q = quarter.split('-Q')
    year = int(year)
    quarter_end_dates = {
        '1': '-03-31',
        '2': '-06-30',
        '3': '-09-30',
        '4': '-12-31'
    }

    if q in quarter_end_dates:
        return f"{year}{quarter_end_dates[q]}"
    else:
        raise ValueError("Invalid quarter format. Use format YYYY-Q<1-4>.")
