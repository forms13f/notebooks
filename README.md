# Forms13F.com API Python Notebooks

This repository contains Jupyter notebooks with examples on how to retrieve information on the latest holdings of funds and view their history of purchases of securities.

## About

These Python notebooks utilize the [Forms13F.com](https://forms13f.com) API to demonstrate how to access and analyze data from Form 13F filings.

## What is Form 13F?

Form 13F is a quarterly report filed by institutional investment managers with the U.S. Securities and Exchange Commission (SEC). It discloses the holdings of equity securities under management, providing transparency into the investment activities of large institutional investors.

## Notebooks

- [`api-examples.ipynb`](api-examples.ipynb) contains examples on how to use the Forms13F Python SDK in Jupyter notebooks.
- [`reports.ipynb`](reports.ipynb) contains examples on how to retrieve historical data on a fund's holdings.

## Resources

- [Forms13F.com](https://forms13f.com)
- [Python SDK for Forms13F.com API](https://github.com/forms13f/python-sdk)
- [Forms13F.com API Documentation](https://forms13f.github.io/api-docs/)
- [Latest Forms 13F Published](https://forms13f.com/pages/latest.html)
- [List of Most Popular Funds](https://forms13f.com/pages/popular.html)

## Setting up Virtual Environment for python

```bash
conda create -n ipynb_env python=3.8
# location ~/opt/anaconda3/envs/ipynb_env
conda activate ipynb_env
conda install ipython jupyter
jupyter notebook 2>&/dev/null