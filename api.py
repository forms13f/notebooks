
import forms13f 
from collections import defaultdict



# Create api client with exponential backoff for 429 responses
api_client = forms13f.ApiClient(n_retries=5)
api_instance = forms13f.DefaultApi(api_client)

# Get fund CIK (Central Index Key) by name substring
def getCIKsByName(name):
    offset = 0  # Integer | Skip previous offset companies (optional) (default to 0)
    limit = 10  # Integer | Return max limit companies (optional) (default to 100)
    
    api_response = api_instance.api_v1_funds_get(name=name, offset=offset, limit=limit)
    
    return [fund.cik for fund in api_response]

# Find the last report available for a given CIK
def getLastReportPeriod(cik):
    from_date = "2010-01-01"  # String | All forms returned will be on or after this period of report date. (optional) (default to 2010-01-01)
    to_date = "2030-01-01"  # String | All forms returned will be on or before this period of report date. (optional) (default to 2030-01-01)
    offset = 0  # Integer | Skip the first offset forms. (optional) (default to 0)
    limit = 1  # Integer | Return at most limit forms. (optional) (default to 100)

    api_response = api_instance.api_v1_forms_get(cik, from_date, to_date, offset=offset, limit=limit)
    
    if api_response:
     return api_response[0].period_of_report
    else:
        return None


# Find all forms 13F filed (including amendments) for a given period of report
# period_of_report is in the form of "YYYY-MM-DD" 
def getFormsForPeriod(cik, period_of_report):
    from_date = period_of_report  # String | All forms returned will be on or after this period of report date.
    to_date = period_of_report  # String | All forms returned will be on or before this period of report date.
    offset = 0  # Integer | Skip the first offset forms. (optional) (default to 0)
    limit = 250  # Integer | Return at most limit forms. (optional) (default to 100)

    api_response = api_instance.api_v1_forms_get(cik, from_date, to_date, offset=offset, limit=limit)
    
    
    # Sort the reports by filed_as_of_date in ascending order
    sorted_reports = sorted(api_response, key=lambda report: report.filed_as_of_date)
    
    return sorted_reports



    wait_time = 0.1  # Start with 100ms
    for attempt in range(n_retries):
        try:
            return func()
        except ApiException as e:
            if e.status == 429:
                print(f"Attempt {attempt + 1} failed with status 429. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, 1)  # Exponential backoff, max 1 second
            else:
                raise e
    # If all retries fail, raise the last exception
    return func()
# Get holdings for a given Form 13F
def getHoldings(cik, accession_number):
    offset = 0
    limit = 250
    all_holdings = []

    while True:

        api_response = api_instance.api_v1_form_get(accession_number, cik, offset=offset, limit=limit)
    
    
        if not api_response:
            break
        
        all_holdings.extend(api_response)
        offset += limit

    # Group holdings by cusip and aggregate value and ssh_prnamt
    holdings_by_cusip = defaultdict(lambda: {
        'accession_number': None,
        'cik': None,
        'name_of_issuer': None,
        'title_of_class': None,
        'cusip': None,
        'value': 0,
        'ssh_prnamt': 0,
        'ssh_prnamt_type': None,
        'investment_discretion': None,
        'voting_authority_sole': 0,
        'voting_authority_shared': 0,
        'voting_authority_none': 0
    })

    for holding in all_holdings:
        cusip = holding.cusip
        if holdings_by_cusip[cusip]['accession_number'] is None:
            holdings_by_cusip[cusip]['accession_number'] = holding.accession_number
            holdings_by_cusip[cusip]['cik'] = holding.cik
            holdings_by_cusip[cusip]['name_of_issuer'] = holding.name_of_issuer
            holdings_by_cusip[cusip]['title_of_class'] = holding.title_of_class
            holdings_by_cusip[cusip]['cusip'] = holding.cusip
            holdings_by_cusip[cusip]['ssh_prnamt_type'] = holding.ssh_prnamt_type
            holdings_by_cusip[cusip]['investment_discretion'] = holding.investment_discretion
        
        holdings_by_cusip[cusip]['value'] += holding.value
        holdings_by_cusip[cusip]['ssh_prnamt'] += holding.ssh_prnamt
        holdings_by_cusip[cusip]['voting_authority_sole'] += holding.voting_authority_sole
        holdings_by_cusip[cusip]['voting_authority_shared'] += holding.voting_authority_shared
        holdings_by_cusip[cusip]['voting_authority_none'] += holding.voting_authority_none

    # Convert the aggregated holdings to a list of ApiV1FormGet200ResponseInner objects
    unique_holdings = [
        forms13f.ApiV1FormEntry(
            accession_number=holding['accession_number'],
            cik=holding['cik'],
            name_of_issuer=holding['name_of_issuer'],
            title_of_class=holding['title_of_class'],
            cusip=holding['cusip'],
            value=holding['value'],
            ssh_prnamt=holding['ssh_prnamt'],
            ssh_prnamt_type=holding['ssh_prnamt_type'],
            investment_discretion=holding['investment_discretion'],
            voting_authority_sole=holding['voting_authority_sole'],
            voting_authority_shared=holding['voting_authority_shared'],
            voting_authority_none=holding['voting_authority_none']
        )
        for holding in holdings_by_cusip.values()
    ]

    # Sort the unique holdings by name_of_issuer
    sorted_holdings = sorted(unique_holdings, key=lambda holding: holding.name_of_issuer)
    
    return sorted_holdings

# given holdings from multiple reports including amendments,
#  consolidate them into a single holdings list
def consolidateHoldings(reports):
    if not reports:
        return []

    # Ensure all reports have the same period_of_report
    period_of_report = reports[0].period_of_report
    for report in reports:
        if report.period_of_report != period_of_report:
            raise ValueError("All reports must have the same period_of_report")

    # Sort reports by filed_as_of_date ASC
    sorted_reports = sorted(reports, key=lambda report: report.filed_as_of_date)

    # Ensure there is 0 or one report with is_amendment=None and it must be the first in the sorted list
    non_amendment_reports = [report for report in sorted_reports if report.is_amendment is None]
    if len(non_amendment_reports) > 1:
        raise ValueError("There must be at most one report with is_amendment=None")
    if non_amendment_reports and non_amendment_reports[0] != sorted_reports[0]:
        raise ValueError("The report with is_amendment=None must be the first in the sorted list")

    # Start with the first in the list as final_report
    final_report = sorted_reports[0]
    final_holdings = getHoldings(final_report.cik, final_report.accession_number)

    # Iterate over remaining items in the list
    for report in sorted_reports[1:]:
        if report.amendment_type == 'RESTATEMENT':
            final_report = report
            final_holdings = getHoldings(report.cik, report.accession_number)
        elif report.amendment_type == 'NEW HOLDINGS':
            new_holdings = getHoldings(report.cik, report.accession_number)
            final_holdings.extend(new_holdings)

    # Sort the final holdings by name_of_issuer
    final_holdings = sorted(final_holdings, key=lambda holding: holding.name_of_issuer)

    return final_holdings

# Given quarter int he form of YYYY-Q<quarter>, and CIK,
#  return the consolidated holdings for that quarter
def getQuarterReport(quarter, cik):
    # Convert the quarter to the period of report
    period_of_report = quarterToPeriodOfReport(quarter)
    
    # Get the reports for the given CIK and period of report
    reports = getFormsForPeriod(cik, period_of_report)
    
    # Consolidate the holdings from the reports
    holdings = consolidateHoldings(reports)
    
    return holdings



