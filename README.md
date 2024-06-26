STILL A WORK IN-PROGRESS

This repo contains code to parse Wealthsimple statement PDFs and save the data in running ledgers. This code was written prior to Wealthsimple making csv document available.

**General Information:**

*build/* contains the python script to read Wealthsimple statements. It has been tested on my TFSA documents for the years 2020 -- current. It is not perfect, but it will try and catch errors and ask for input if it gets stuck.

*data/* is where your statement information is stored. Within this dir:
- *cash_paid_in.csv* summarizes the information (per statement) from the "Cash Paid In" section,
- *cash_paid_out.csv* summarizes the information (per statement) from the "Cash Paid Out" section,
- *holdings.csv* summarizes the information (per statement) in the "Portfolio Equities" section, and
- *info.csv* contains info on each equity you hold (ticker, region, sector, type). You do not need to touch this document, it updates itself.

*statements/* is a dir for your statements. I recommend the two sub dirs: *read/* and *unread/* to sort the statements you have processed and the ones you have not.

**Dependencies:**

I built and tested this code using Python 3.12.1. The python scripts require numpy, pandas, pypdf2, scipy, and matplotlib.

**How to run:**
- Clone this repo.
- Download your Wealthsimple statements and put them in *statements/unread/*. **Note** the number of words in your name under "Owner" in the header of the Wealthsimple statement, this will be used below.
- To read the statements, run: *python build/read_pdf.py statements/unread/{statement} {# of words in your name under Owner in the header of the Wealthsimple statement}*
- Assuming no errors, move these statements from *unread/* to *read/*
- To get a summary of the most recent statement, run: *python build/summary.py*

