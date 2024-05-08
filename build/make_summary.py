import pandas as pd
import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt

def plot_return(df):
    # Calculate cumulative sum of 'Deposits' column
    df['Cumulative Deposits'] = df['Deposits'].cumsum()
    # Calculate 'Return' column
    df['Return'] = df['Total Portfolio'] - df['Cumulative Deposits']
    # Create a plot
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df['Return'], marker='o', color='b', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Return ($)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()



def calc_annual_compounded_rate(df, total_portfolio_value):
    # Convert 'Date' column to datetime
    # taking the 'Start' of statement period to be the deposit date, even
    # though its between 'Start' and 'End'
    df['Date'] = pd.to_datetime(df['Start'])
    
    # Calculate the time difference in years
    # (most recent date) - (deposit date) <- converted to years
    df['Years_Invested'] = ((df['Date'].max() - df['Date']).dt.days)/365
    
    # Define the objective function to minimize
    def objective_function(rate):
        # taking absolute values ensures that the objective_function is is >= 0
        # .mul is element-wise multiplication
        # this looks like (deposit value)*(rate of return)^(years deposit is invested)
        # summed over all deposits
        return np.abs(df['Deposits'].mul((1 + rate)**(df['Years_Invested'])).sum() 
                      - total_portfolio_value)

    # Find the rate that minimizes the difference between the sum of compounded 
    # deposits and the total portfolio value. NOTE, I am assuming here that
    # your rate is between 0 and 100% (compounded annually), if you have a
    # greater performance than this, change the bounds to (0,x) where x is your
    # maximum possible compounded rate of return
    result = minimize_scalar(objective_function, method='bounded', bounds=(0, 1))
    
    # The result x is the annual compounded rate
    annual_compounded_rate = result.x*100

    # sanity check
    value = 0
    for index, row in df.iterrows():
        value += row['Deposits']*((1+result.x)**row['Years_Invested'])
    if value > total_portfolio_value - 1 and value < total_portfolio_value + 1:
        pass
    else:
        print("Expected value: {} =?= {} (actual value)".format(value, total_portfolio_value))

    return annual_compounded_rate


def main():
    holdings_df = pd.read_csv("data/holdings.csv")
    cash_in_df = pd.read_csv("data/cash_paid_in.csv")

    cash_in_df['Start'] = pd.to_datetime(cash_in_df['Start'])
    cash_in_df['End'] = pd.to_datetime(cash_in_df['End'])

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


    print("\n---------------------- {} HOLDINGS ----------------------".format(recent_statement))
    print(holdings_df[["Ticker", "Return (%)", "Return ($)", "% of portfolio", "Quantity", "Value ($)"]].to_string(index=False))
    print("Cash: ${:.2f}".format(cash_in_df[cash_in_df.End == recent_statement].Cash.values[0]))
    print("-----------------------------------------------------------------\n")


    sector_df = holdings_df.groupby(by = "sector")['Value ($)'].sum().reset_index()
    sector_df["% of portfolio"] = (sector_df['Value ($)']/port_value)*100
    sector_df.sort_values(by="% of portfolio", ascending=False, inplace=True)
    sector_df.rename(columns={'sector': 'Sector'}, inplace=True)

    print("---------------------- {} SECTOR  -----------------------".format(recent_statement))
    print(sector_df[["Sector", "% of portfolio"]].to_string(index=False))
    print("----------------------------------------------------------------\n")


    region_df = holdings_df.groupby(by = "region")['Value ($)'].sum().reset_index()
    region_df["% of portfolio"] = (region_df['Value ($)']/port_value)*100
    region_df.sort_values(by="% of portfolio", ascending=False, inplace=True)
    region_df.rename(columns={'region': 'Region'}, inplace=True)

    print("---------------------- {} REGION  ----------------------".format(recent_statement))
    print(region_df[["Region", "% of portfolio"]].to_string(index=False))
    print("\nDesired: 25% CAD, 35% US, 15% INT, 25% Fixed")
    print("----------------------------------------------------------------\n")


    print("---------------------- PERFORMACE SUMMARY ----------------------")
    print("Deposits: ${:.2f}".format(cash_in_df.Deposits.sum()))
    print("Portfolio Value: ${:.2f}".format(port_value))
    print("Return ($): ${:.2f}".format(port_value-cash_in_df.Deposits.sum()))
    print("Return (%): {:.2f}%".format((port_value/cash_in_df.Deposits.sum() -1)*100))
    print("Total Annual compounded return (%): {:.2f}%".format(
          calc_annual_compounded_rate(cash_in_df, port_value)))
    print("-----------------------------------------------------------------\n")

    print("---------------------- DIVIDENDS AND TAXES  ----------------------")
    print("Dividends: ${:.2f}".format(cash_in_df.Dividends.sum()))
    print("Taxes: ${:.2f}".format(cash_out_df.Taxes.sum()))
    print("------------------------------------------------------------------")

    plot_return(cash_in_df)

main()
