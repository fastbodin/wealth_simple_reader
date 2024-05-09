import pandas as pd
import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt


def plot_return_percent(df, df_out):
    # Calculate cumulative sum of 'Deposits' column
    df['Cumulative Deposits'] = df['Deposits'].cumsum()
    # Calculate cumulative sum of 'Withdrawals' column
    df_out['Cumulative Withdrawals'] = df_out["Withdrawals"].cumsum()
    # Calculate 'Return' column
    df['Return'] = (df['Total Portfolio'] - df['Cumulative Deposits']
                    + df_out["Cumulative Withdrawals"])/df['Cumulative Deposits']

    fig, ax1 = plt.subplots()
    # Plotting the 'Return' data on the primary y-axis
    ax1.plot(df['Date'], df['Return'], marker='o', color='b', linestyle='-', label='Return')
    ax1.set_ylabel('Return (%)')
    ax1.set_xlabel('Date')
    ax1.tick_params(axis='y')
    yticks=ax1.get_yticks()
    ylabels = ["{:.1f}".format(tick*100) for tick in yticks]
    ax1.set_yticks(ticks = yticks, labels = ylabels)


    # Creating a secondary y-axis for 'Cumulative Deposits'
    ax2 = ax1.twinx()
    ax2.plot(df['Date'], df['Cumulative Deposits']-df_out["Cumulative Withdrawals"], 
             marker='o', color='r', linestyle='-', label='Deposits-Withdrawals')
    ax2.set_ylabel('Cumulative Deposits - Cumulative Withdrawals ($)')
    ax2.tick_params(axis='y')

    # Adding legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    ax1.grid(True)
    fig.tight_layout()
    plt.show()

def plot_return_money(df, df_out):
    # Calculate cumulative sum of 'Deposits' column
    df['Cumulative Deposits'] = df['Deposits'].cumsum()
    # Calculate cumulative sum of 'Withdrawals' column
    df_out['Cumulative Withdrawals'] = df_out["Withdrawals"].cumsum()
    # Calculate 'Return' column
    df['Return'] = (df['Total Portfolio'] - df['Cumulative Deposits']
                    + df_out["Cumulative Withdrawals"])
    # Create a plot
    fig, ax1 = plt.subplots()
    # Plotting the 'Return' data on the primary y-axis
    ax1.plot(df['Date'], df['Return'], marker='o',color='b',linestyle='-',label='Return')
    ax1.set_ylabel('Return ($)')
    ax1.set_xlabel('Date')
    ax1.tick_params(axis='y')

    # Creating a secondary y-axis for 'Cumulative Deposits'
    ax2 = ax1.twinx()
    ax2.plot(df['Date'], df['Cumulative Deposits']-df_out["Cumulative Withdrawals"], 
             marker='o', color='r', linestyle='-', label='Deposits-Withdrawals')
    ax2.set_ylabel('Cumulative Deposits - Cumulative Withdrawals ($)')
    ax2.tick_params(axis='y')

    # Adding legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    ax1.grid(True)
    fig.tight_layout()
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
    for _, row in df.iterrows():
        value += row['Deposits']*((1+result.x)**row['Years_Invested'])
    if (value > total_portfolio_value - 1 and 
        value < total_portfolio_value + 1):
        pass
    else:
        print("Expected value: {} =?= {} (actual value)".format(value,
              total_portfolio_value))

    return annual_compounded_rate


def main():
    # read in data
    holdings_df = pd.read_csv("data/holdings.csv")
    cash_in_df = pd.read_csv("data/cash_paid_in.csv")
    cash_out_df = pd.read_csv("data/cash_paid_out.csv")
    # make sure everything is ordered correctly by data
    cash_in_df.sort_values(by="End",inplace=True)
    cash_out_df.sort_values(by="End",inplace=True)
    # grab the most recent date
    cur_period = cash_in_df.End.values[-1]
    # grab current holdings
    holdings_df = holdings_df[holdings_df.date == cur_period]
    # current portfolio value
    cur_port_value = cash_in_df.loc[cash_in_df.End == cur_period]["Total Portfolio"].values[0]
    # total portfolio value is equal to current Total Portfolio value plus all
    # withdrawals (== crystalied gains)
    tot_port_value = cur_port_value + cash_out_df.Withdrawals.sum()
    # calculate % of portfolio and return ($,%) for each holding
    holdings_df["% of portfolio"] = (holdings_df.market_value/cur_port_value)*100
    holdings_df["Return (%)"] = (holdings_df.market_value/holdings_df.book_cost - 1)*100
    holdings_df["Return ($)"] = (holdings_df.market_value - holdings_df.book_cost)
    holdings_df.sort_values(by="Return (%)", ascending=False, inplace=True)
    # for nicer formatting
    holdings_df.rename(columns={'ticker': 'Ticker'}, inplace=True)
    holdings_df.rename(columns={'market_value': 'Value ($)'}, inplace=True)
    holdings_df.rename(columns={'total_quantity': 'Quantity'}, inplace=True)

    print("\n---------------------- {} HOLDINGS ----------------------".format(cur_period))
    print(holdings_df[["Ticker", "Return (%)", "Return ($)", "% of portfolio", "Quantity", "Value ($)"]].to_string(index=False))
    print("Cash: ${:.2f}".format(cash_in_df[cash_in_df.End == cur_period].Cash.values[0]))
    print("-----------------------------------------------------------------\n")

    sector_df = holdings_df.groupby(by = "sector")['Value ($)'].sum().reset_index()
    sector_df["% of portfolio"] = (sector_df['Value ($)']/cur_port_value)*100
    sector_df.sort_values(by="% of portfolio", ascending=False, inplace=True)
    sector_df.rename(columns={'sector': 'Sector'}, inplace=True)

    print("---------------------- {} SECTOR  -----------------------".format(cur_period))
    print(sector_df[["Sector", "% of portfolio"]].to_string(index=False))
    print("----------------------------------------------------------------\n")

    region_df = holdings_df.groupby(by = "region")['Value ($)'].sum().reset_index()
    region_df["% of portfolio"] = (region_df['Value ($)']/cur_port_value)*100
    region_df.sort_values(by="% of portfolio", ascending=False, inplace=True)
    region_df.rename(columns={'region': 'Region'}, inplace=True)

    print("---------------------- {} REGION  ----------------------".format(cur_period))
    print(region_df[["Region", "% of portfolio"]].to_string(index=False))
    print("\nDesired: 25% CAD, 35% US, 15% INT, 25% Fixed")
    print("----------------------------------------------------------------\n")

    print("---------------------- PERFORMACE SUMMARY ----------------------")
    print("Deposits: ${:.2f}".format(cash_in_df.Deposits.sum()))
    print("Withdrawals: ${:.2f}".format(cash_out_df.Withdrawals.sum()))
    print("Current Portfolio Value: ${:.2f}".format(cur_port_value))
    print("Total Return ($): ${:.2f}".format(tot_port_value-cash_in_df.Deposits.sum()))
    print("Total Return (%): {:.2f}%".format((tot_port_value/cash_in_df.Deposits.sum()-1)*100))
    print("Total Annual compounded return (%): {:.2f}%".format(
          calc_annual_compounded_rate(cash_in_df, tot_port_value)))
    print("-----------------------------------------------------------------\n")

    print("---------------------- DIVIDENDS AND TAXES  ----------------------")
    print("Dividends: ${:.2f}".format(cash_in_df.Dividends.sum()))
    print("Taxes: ${:.2f}".format(cash_out_df.Taxes.sum()))
    print("------------------------------------------------------------------")

    plot_return_percent(cash_in_df, cash_out_df)
    plot_return_money(cash_in_df, cash_out_df)

main()


    #cash_in_df['Start'] = pd.to_datetime(cash_in_df['Start'])
    #cash_in_df['End'] = pd.to_datetime(cash_in_df['End'])
    #cash_out_df['Start'] = pd.to_datetime(cash_out_df['Start'])
    #cash_out_df['End'] = pd.to_datetime(cash_out_df['End'])
