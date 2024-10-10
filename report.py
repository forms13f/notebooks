from datetime import date
from typing import List, Optional
from api import *
import forms13f
from forms13f.util import quarterToPeriodOfReport


class ReportHeader:
    def __init__(self, urls: List[str], accession_numbers: List[str], submission_type: str, public_document_count: int,
                 period_of_report: date, report_quarter: str, filing_dates: List[date], date_as_of_change: date, effectiveness_date: date,
                 cik: str, company_name: str, irs_number: str, state_of_incorporation: str, fiscal_year_end: str,
                 form_type: str, sec_act: str, business_address: str,
                 business_phone: str, table_value_total: int, table_entry_total: int):
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

class QuarterReport:
    def __init__(self, header: ReportHeader, holdings: List[forms13f.ApiV1FormEntry]):
        self.header = header
        self.holdings = holdings

def getQuarterReport(quarter, cik):
    # Convert the quarter to the period of report
    period_of_report = quarterToPeriodOfReport(quarter)
    
    # Get the reports for the given CIK and period of report
    reports = getFormsForPeriod(cik, period_of_report)
    
    # Aggregate the holdings from the reports
    holdings = consolidateHoldings(reports)
    
    # Create the header
    urls = [report.url for report in reports]
    accession_numbers = [report.accession_number for report in reports]
    filing_dates = [report.filed_as_of_date for report in reports]
    first_report = reports[0]
    
    header = ReportHeader(
        urls=urls,
        accession_numbers=accession_numbers,
        submission_type=first_report.submission_type,
        public_document_count=first_report.public_document_count,
        period_of_report=first_report.period_of_report,
        report_quarter=quarter,
        filing_dates=filing_dates,
        date_as_of_change=first_report.date_as_of_change,
        effectiveness_date=first_report.effectiveness_date,
        cik=first_report.cik,
        company_name=first_report.company_name,
        irs_number=first_report.irs_number,
        state_of_incorporation=first_report.state_of_incorporation,
        fiscal_year_end=first_report.fiscal_year_end,
        form_type=first_report.form_type,
        sec_act=first_report.sec_act,
        business_address=first_report.business_address,
        business_phone=first_report.business_phone,
        table_value_total=first_report.table_value_total,
        table_entry_total=first_report.table_entry_total,
     )
    
    # Create the QuarterReport
    quarter_report = QuarterReport(header=header, holdings=holdings)
    
    return quarter_report

