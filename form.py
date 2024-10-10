import forms13f
from collections import defaultdict

# Create api client with exponential backoff for 429 responses
api_client = forms13f.ApiClient(n_retries=5)
api_instance = forms13f.DefaultApi(api_client)


class Form:
    """
    A class to represent a financial form and its associated holdings.

    Attributes:
        header (forms13f.ApiV1Form): The header information of the form.
        holdings (list): A list of holdings associated with the form.

    Methods:
        __init__(header, cik, accession_number):
            Initializes the Form object with header, CIK, and accession number.

        _get_holdings(cik, accession_number):
            Retrieves and consolidates holdings for the given CIK and accession number.

        consolidate_holdings(forms):
            Static method to consolidate holdings from an array of Form objects.
    """

    def __init__(self, header: forms13f.ApiV1Form, cik: str, accession_number: str):
        self.header = header
        self.holdings = self._get_holdings(cik, accession_number)

    def _get_holdings(self, cik, accession_number):
        offset = 0
        limit = 250
        all_holdings = []

        while True:
            api_response = api_instance.api_v1_form_get(accession_number, cik, offset=offset, limit=limit)

            if not api_response:
                break

            all_holdings.extend(api_response)
            offset += limit

        holdings_by_cusip = defaultdict(lambda: {
            'accession_number': None,
            'cik': None,
            'ticker': None,
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
                holdings_by_cusip[cusip]['ticker'] = holding.ticker
                holdings_by_cusip[cusip]['ssh_prnamt_type'] = holding.ssh_prnamt_type
                holdings_by_cusip[cusip]['investment_discretion'] = holding.investment_discretion

            holdings_by_cusip[cusip]['value'] += holding.value
            holdings_by_cusip[cusip]['ssh_prnamt'] += holding.ssh_prnamt
            holdings_by_cusip[cusip]['voting_authority_sole'] += holding.voting_authority_sole
            holdings_by_cusip[cusip]['voting_authority_shared'] += holding.voting_authority_shared
            holdings_by_cusip[cusip]['voting_authority_none'] += holding.voting_authority_none

        unique_holdings = [
            forms13f.ApiV1FormEntry(
                accession_number=holding['accession_number'],
                cik=holding['cik'],
                name_of_issuer=holding['name_of_issuer'],
                title_of_class=holding['title_of_class'],
                cusip=holding['cusip'],
                ticker=holding['ticker'],
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

        sorted_holdings = sorted(unique_holdings, key=lambda holding: holding.name_of_issuer)

        return sorted_holdings


@staticmethod
def consolidate_holdings(forms):
    """
    Consolidate holdings from an array of Form objects.

    This method ensures all forms have the same period of report, sorts the forms by their filed_as_of_date,
    and consolidates the holdings considering amendments.

    Args:
        forms (list): A list of Form objects to be consolidated.

    Returns:
        list: A list of consolidated holdings sorted by name_of_issuer.

    Raises:
        ValueError: If forms have different period_of_report or if there are multiple forms with is_amendment=None.
    """
    if not forms:
        return []

    # Ensure all forms have the same period_of_report
    period_of_report = forms[0].header.period_of_report
    for form in forms:
        if form.header.period_of_report != period_of_report:
            raise ValueError("All forms must have the same period_of_report")

    # Sort forms by filed_as_of_date ASC
    form_reports = sorted(forms, key=lambda form: form.header.filed_as_of_date)

    # Ensure there is 0 or one forms with is_amendment=None and it must be the first in the sorted list
    non_amendment_form = [form for form in form_reports if form.header.is_amendment is None]
    if len(non_amendment_form) > 1:
        raise ValueError("There must be at most one form with is_amendment=None")
    if non_amendment_form and non_amendment_form[0] != form_reports[0]:
        raise ValueError("The form with is_amendment=None must be the first in the sorted list")

    # Start with the first in the list as final_report
    final_report = form_reports[0]
    final_holdings = final_report.holdings

    # Iterate over remaining items in the list
    for form in form_reports[1:]:
        if form.header.amendment_type == 'RESTATEMENT':
            final_report = form
            final_holdings = form.holdings
        elif form.header.amendment_type == 'NEW HOLDINGS':
            final_holdings.extend(form.holdings)

    # Sort the final holdings by name_of_issuer
    final_holdings = sorted(final_holdings, key=lambda holding: holding.name_of_issuer)

    return final_holdings


def get_forms_for_period(cik, period_of_report):
    """
    Retrieve and return a list of Form objects for a given CIK and period of report.

    Args:
        cik (str): The Central Index Key (CIK) of the entity for which forms are to be retrieved.
        period_of_report (str): The period of report date in the format 'YYYY-MM-DD'. All forms returned will be on or after this date.

    Returns:
        list: A list of Form objects sorted by their filed_as_of_date in ascending order.
    """
    from_date = period_of_report  # String | All forms returned will be on or after this period of report date.
    to_date = period_of_report  # String | All forms returned will be on or before this period of report date.
    offset = 0  # Integer | Skip the first offset forms. (optional) (default to 0)
    limit = 250  # Integer | Return at most limit forms. (optional) (default to 100)

    api_response = api_instance.api_v1_forms_get(cik, from_date, to_date, offset=offset, limit=limit)

    # Sort the reports by filed_as_of_date in ascending order
    sorted_forms = sorted(api_response, key=lambda form: form.filed_as_of_date)

    # Create Form objects for each sorted form
    form_objects = [Form(header=form, cik=form.cik, accession_number=form.accession_number) for form in sorted_forms]

    return form_objects


def get_ciks_by_name(name):
    """
    Retrieve a list of Central Index Keys (CIKs) for funds that match the given name substring.

    Args:
        name (str): The name substring to search for matching funds.

    Returns:
        list: A list of CIKs for funds that match the given name substring.
    """
    offset = 0  # Integer | Skip previous offset companies (optional) (default to 0)
    limit = 10  # Integer | Return max limit companies (optional) (default to 100)

    api_response = api_instance.api_v1_funds_get(name=name, offset=offset, limit=limit)

    return [fund.cik for fund in api_response]
