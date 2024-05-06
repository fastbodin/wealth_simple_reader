import pandas as pd

def main():
    holdings_df = pd.read_csv("data/holdings.csv")
    cash_in_df = pd.read_csv("data/cash_paid_in.csv")
    cash_out_df = pd.read_csv("data/cash_paid_out.csv")

    recent_statement = holdings_df.date.values[-1]

    holdings_df = holdings_df[holdings_df.date == recent_statement]

    port_value = cash_in_df.loc[cash_in_df.End == recent_statement]["Total Portfolio"].values[0]

    holdings_df["% of portfolio"] = (holdings_df.market_value/port_value)*100
    holdings_df["Return (%)"] = (holdings_df.market_value/holdings_df.book_cost - 1)*100
    holdings_df["Return ($)"] = (holdings_df.market_value - holdings_df.book_cost)
    holdings_df.sort_values(by="Return (%)", ascending=False, inplace=True)

    holdings_df.rename(columns={'ticker': 'Ticker'}, inplace=True)
    holdings_df.rename(columns={'market_value': 'Value ($)'}, inplace=True)
    holdings_df.rename(columns={'total_quantity': 'Quantity'}, inplace=True)


    print("---------------------- {} HOLDINGS ----------------------".format(recent_statement))
    print(holdings_df[["Ticker", "Return (%)", "Return ($)", "% of portfolio", "Quantity", "Value ($)"]].to_string(index=False))
    print("-----------------------------------------------------------------")


    sector_df = holdings_df.groupby(by = "sector")['Value ($)'].sum().reset_index()
    sector_df["% of portfolio"] = (sector_df['Value ($)']/port_value)*100
    sector_df.sort_values(by="% of portfolio", ascending=False, inplace=True)
    sector_df.rename(columns={'sector': 'Sector'}, inplace=True)

    print("---------------------- {} SECTOR  -----------------------".format(recent_statement))
    print(sector_df[["Sector", "% of portfolio"]].to_string(index=False))
    print("----------------------------------------------------------------")


    region_df = holdings_df.groupby(by = "region")['Value ($)'].sum().reset_index()
    region_df["% of portfolio"] = (region_df['Value ($)']/port_value)*100
    region_df.sort_values(by="% of portfolio", ascending=False, inplace=True)
    region_df.rename(columns={'region': 'Region'}, inplace=True)

    print("---------------------- {} REGION  ----------------------".format(recent_statement))
    print(region_df[["Region", "% of portfolio"]].to_string(index=False))
    print("----------------------------------------------------------------")

    print("---------------------- TOTAL SUMMARY  ----------------------")
    print("Value: ${:.2f}".format(port_value))
    print("Cash: ${:.2f}".format(cash_in_df[cash_in_df.End == recent_statement].Cash.values[0]))
    print("Deposits: ${:.2f}".format(cash_in_df.Deposits.sum()))
    print("Dividends: ${:.2f}".format(cash_in_df.Dividends.sum()))
    print("Taxes: ${:.2f}".format(cash_out_df.Taxes.sum()))
    print("------------------------------------------------------------")

main()
