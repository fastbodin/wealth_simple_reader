import sys
import pandas as pd
import numpy as np
from PyPDF2 import PdfReader 



def check_info_equities(pdf_name, period, equities):
    print(equities)
    # read in information csv
    info_df = pd.read_csv("data/info.csv")

    for equity in equities.ticker:
        if equity not in info_df.ticker.values:
            info_df, new_equity = u_input_info(pdf_name, info_df, equity)
            if new_equity != equity:
                equities.loc[(equities.ticker == equity), 'ticker'] = new_equity

    info_df.sort_values(by = "ticker").to_csv("data/info.csv", index = False)

    # Merge equities and info_df based on 'ticker' column
    merged_df = pd.merge(equities, info_df, on='ticker', how='left')

    return merged_df

def update_csv_equity(date, new_df, csv_name):
    # read in old csv
    df = pd.read_csv(csv_name)
    # alphabetize
    new_df = new_df.sort_values(by = 'ticker')
    if (len(df) == 0):
        new_df.to_csv(csv_name, index = False)
        return
    if (len(df.loc[df.date == date]) != 0):
        user_response = u_confirm("Updating {}. There already exists an "
                                  "entry for the date: {}. Would you "
                                  "like to replace it?".format(csv_name, date))
        if user_response == "y":
            df.drop(df[df.date == date].index, inplace=True)
        else:
            warn("Did not update holdings.csv for the date: {}".format(date))
            return
    pd.concat([df, new_df], axis = 0).to_csv(csv_name, index = False)


def update_csv(period, new_row, csv_name):
    # read in old csv
    df = pd.read_csv(csv_name)
    # grab start and end of statement period
    start = period.at[0, "Start"].strftime('%Y-%m-%d')
    end = period.at[0, "End"].strftime('%Y-%m-%d')
    period_n = pd.DataFrame({"Start": [start], "End": [end]})
    if (len(df) == 0):
        pd.concat([period_n, new_row], axis = 1).to_csv(csv_name, index = False)
        return
    if (len(df.loc[(df.Start == start) & (df.End == end)]) != 0):
        user_response = u_confirm("Updating {}. There already exists an "
                                  "entry for the statement period: {}, {}. Would you "
                                  "like to replace it?".format(csv_name, start, end))
        if user_response == "y":
            df.drop(df[(df.Start == start) & (df.End == end)].index, inplace=True)
        else:
            warn("Did not update cash_paid_in.csv for the statement period: {} {}"
                 .format(start, end))
            return

    pd.concat([df, pd.concat([period_n, new_row], axis = 1)], axis = 0).sort_values(
                             by = "Start").to_csv(csv_name, index = False)


def within_one_cent(val1, val2):
    if val1 + 0.01 >= val2 and val1 - 0.01 <= val2:
        return True
    return False

def sum_round_by_two(values):
    sum_val = 0
    for i in range(len(values)):
        sum_val += round(values[i], 2)
    return round(sum_val, 2)

def error_system_exit(error_type):
    print("-------------------------------------------------")
    print("Error: {}. Program quit".format(error_type))
    print("-------------------------------------------------")
    sys.exit()

def warn(warning_statement):
    print("-------------------------------------------------")
    print("Warning: {}.".format(warning_statement))
    print("-------------------------------------------------")

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except:
        error_system_exit(("Unexpected error when evaluating if "
                           "input: {} is integer".format(s)))

def u_confirm(user_query):
    return input("{} (y, n) ".format(user_query))

def u_input_info(pdf_name, info_df, equity):
    print("Missing information on {}. Please answer the following.".format(equity))

    t_confirm = u_confirm("Is the ticker: {} correct?".format(equity))
    if t_confirm == "n":
        new_equity = u_input("Lets update it then.\nTicker <- case sens.):", "")
        equity = new_equity

    confirm = 'n'
    while confirm == 'n':
        region = u_input("Region (US, CAN, INT, etc. <- case sens.):", "")
        e_type = u_input("Type (stock, bond, ETF, etc. <- case sens.):", "")
        sector = u_input("Sector (tech, finance, etc. <- case sens.):", "")
        # add missing equity
        row = pd.DataFrame({"ticker": [equity],
                            "region": [region],
                            "sector": [sector],
                            "type": [e_type]})
        confirm = u_confirm("Is the following correct? Ticker: {}, region: {}, "
                            "sector: {}, type: {}".format(equity,region,sector,e_type))
        if confirm == 'n':
            print("Lets try this again")

    # update the entry of the equity
    info_df = update_df_row(pdf_name, [equity], ["ticker"], row, info_df)
    info_df.reset_index(drop = True, inplace = True)
    return info_df, equity


def u_input(query, return_type):
    value = input("{} ".format(query))
    value = rem_char(value, [',', '$'])
    if return_type == "%Y-%m-%d":
        try:
            value = pd.to_datetime(value, format='%Y-%m-%d')
            return value
        except:
            error_system_exit("Incorrect User Input: ({})".format(value))
    elif return_type == "":
        return(value)
    elif return_type == "all_caps":
        if not value.isupper():
            error_system_exit("Incorrect User Input: {}. Not uppercase".format(value))
        return value
    elif type(return_type()) == type(float()):
        if not is_int(rem_char(value, ["."])):
            error_system_exit("Incorrect User Input: {}. Not float.".format(value))
    elif type(return_type()) == type(int()):
        if not is_int(value):
            error_system_exit("Incorrect User Input: {}. Not int.".format(value))
    return return_type(value)

def u_input_equity(pdf_name, equities, date, replace, index):
    ticker = u_input("Ticker: ", "all_caps")
    total_quantity = u_input("Total Quantity: ", float)
    market_price = u_input("Market Price: ", float)
    cur = u_input("Currency: ", "all_caps")
    market_value = u_input("Market Value: ", float)
    book_cost = u_input("Book Cost: ", float)
    # if replacing row
    if replace:
        equities.drop(index = index, inplace = True)
    # add missing equity
    ticker_row = pd.DataFrame({"date": [date],
                               "ticker": [ticker], 
                               "total_quantity": [total_quantity], 
                               "market_price": [market_price], 
                               "currency": [cur], 
                               "market_value": [market_value], 
                               "book_cost": [book_cost], 
                               })
    # update the entry of the equity
    equities = update_df_row(pdf_name, [ticker], ["ticker"], ticker_row, equities)
    equities.reset_index(drop = True, inplace = True)
    return equities

def u_query(user_query_1, user_query_2, return_type):
    user_response = u_confirm(user_query_1)
    if user_response == "y":
        if user_query_2 != False:
            return True, True
        else:
            return True
    elif user_response == "n":
        if user_query_2 != False:
            return False, u_input(user_query_2, return_type)
        else:
            return False
    else:
        error_system_exit("Incorrect User Input: ({})".format(user_response))

def rem_char(word, chars):
    for char in chars:
        word = word.replace(char, '')
    return word

def concat_before_find(word, char, shift):
    return word[:word.find(char)+shift]

def concat_after_find(word, char, shift):
    return word[word.find(char)+shift:]

def join_text_no_space(text, start, end):
    try:
        return "".join(text[j] for j in range(start, end+1)) 
    except IndexError:
        pass
    except:
        error_system_exit(("Unexpected error when joining PDF"
                           " from indicies {} to {}".format(start, end)))

def join_text_space(text, start, end):
    try:
        return " ".join(text[j] for j in range(start, end+1)) 
    except IndexError:
        pass
    except:
        error_system_exit("Unexpected error when joining PDF"
                          " from indicies {} to {}".format(start, end))

def cursor_at_phrase(text, index, phrase):
    num_word = phrase.count(' ') + 1
    num_char = len(phrase)
    if num_word == 1:
        if text[index][-num_char:] == phrase:
            return True
        else:
            return False
    else:
        if join_text_space(text, index, index + num_word)[-num_char:] == phrase:
            return True
        return False

def convert_to_date_time(pdf_name, period, date):
    try:
        date = pd.to_datetime(date, format='%Y-%m-%d').date()
        return date
    except:
        # cannot assign date
        warn("Warning. PDF: {}\nCannot determine Statement period {}"
             .format(pdf_name,period))
        return u_input("Please type correct date (YYYY-MM-DD): ", '%Y-%m-%d')

# hacky way to get the date since, when reading the pdf,
# spaces end up in odd spots sometimes...
def hacky_get_date(pdf_name, text, start_index, period):
    date = ""
    i = 0
    # date will be 10 characters (no spaces)
    while len(date) < 10:
        date = join_text_space(text, start_index, start_index + i).replace(" ", "")
        i += 1
    # if it is over 10 characters, should be the last 10
    if len(date) != 10:
        date = date[-10:]
    # make sure the date was actually determined
    date = convert_to_date_time(pdf_name, period, date)
    return date, start_index + i

def update_df_col_row(pdf_name, entry_col, new_entry, data_frame):
    if np.isnan(data_frame.at[0, entry_col]):
        data_frame.at[0, entry_col] = new_entry        
        return data_frame 
    # entry has already been written
    warn("Warning. PDF: {}\nAssignment of {} already exists:\n{}\n"
         .format(pdf_name, entry_col, data_frame[entry_col][0]))
    user_response = u_confirm("Would you like to replace with:\n{}".format(new_entry))
    if user_response == "y":
        data_frame.at[0, entry_col] = new_entry        
        return data_frame 
    elif user_response == "n":
        return data_frame
    else:
        error_system_exit("Incorrect User Input: ({})".format(user_response))

def update_df_row(pdf_name, entries, entries_columns, entries_row, data_frame):
    # if data frame is empty, then there are no row conflicts
    if len(data_frame) == 0:
        return entries_row
        #return pd.concat([data_frame, entries_row])    
    # check if columns of entries exist
    for col in entries_columns:
        if col not in data_frame.columns:
            error_system_exit("Incorrect column label: ({}). "
                              "Expected label in ({})".format(col, data_frame.columns))
    # reduce the data frame to the rows for which every 'entry' (in its respective
    # column) is found, note that their may be multiple 'entries'
    equality_f = '{0[0]} == "{0[1]}"'.format
    # note that there will only be at most one duplicate row since this function
    # is always called when updated a data frame row
    duplicate_row = data_frame.query(' & '.join(equality_f(i) for i in 
                                     zip(entries_columns, entries))).index
    # there is no such row
    if len(duplicate_row) == 0:
        return pd.concat([data_frame, entries_row])

    # there exists a row with this information already,
    warn("Warning. PDF: {}\nAssignment of {} in column {} already exists:\n{}\n"
         .format(pdf_name, entries, entries_columns, data_frame.iloc[duplicate_row[0]]))
    user_response = u_confirm("Would you like to replace with:\n{}\n"
                              .format(entries_row.T))
    if user_response == "y":
        # delete old row entries
        data_frame.drop([duplicate_row[0]], inplace = True)
        # add new row entries
        return pd.concat([data_frame, entries_row])
    elif user_response == "n":
        return data_frame
    else:
        error_system_exit("Incorrect User Input: ({})".format(user_response))

def found_date(pdf_name, text, index, num_word_name):
    # find start date
    start, end_shift = hacky_get_date(pdf_name, text, index+3+num_word_name, "Start")
    # find end date. 
    # there should be a "-" in between Start and End dates, hence add +1 to end_shift
    end, _ = hacky_get_date(pdf_name, text, end_shift + 1, "End")

    return start, end

# function for Cash Paid In and Cash Paid Out items
def found_cash_paid_item(text, index, cash_df):
    # grab the column headers of cash data frame
    cash_cols = cash_df.columns
    # iterate over the "Cash Paid -" information 
    for col_item in cash_cols:
        # if first word is not 'col' and second does not contain '$'
        if not (cursor_at_phrase(text, index, col_item) and text[index+1][0] == "$"):
            continue
        # found the item and cash value corresponding to 'col'
        item_val = float(rem_char(concat_before_find(text[index+1], '.', 3), [',', '$']))
        # return 
        return True, col_item, item_val
    # did not find any instances of "Cash Paid -" items
    return False, False, False

    # sometimes there are issues with extra spaces
def search_till_dot_before_cents(text, index, max_shift):
    shift = 0
    value = join_text_no_space(text, index, index+shift)
    while (len(value) - value.find(".") != 3):
        if shift > max_shift:
            break
        shift += 1
        value = join_text_no_space(text, index, index+shift)
    value = concat_after_find(value, "$", 0)
    return rem_char(value, [',', '$']), index+shift

def reduce_till_uppper(text):
    while not text.isupper():
        text = text[1:]
        if text == "":
            break
    return text

# for finding portfolio equity
def found_equity(text, index, date):
    # symbol is uppercase
    ticker = rem_char(reduce_till_uppper(text[index]), ['(', ')'])
    if ticker == "":
        return False, False
    # next entries should be "Total Quantity", 
    if not is_int(rem_char(text[index+1], ['.', ','])):
        return False, False
    total_quantity = float(rem_char(text[index+1], [',']))
    # next entries should be "Segregated Quantity"
    if not is_int(rem_char(text[index+2], ['.', ','])):
        return False, False
    # next entries should be "Market Price"
    market_price, index = search_till_dot_before_cents(text, index+3, 3)
    market_price = concat_before_find(market_price, '.', 3)
    if not is_int(rem_char(market_price, ['.'])):
        return False, False
    market_price = float(market_price)
    # next entry should be currency
    cur = reduce_till_uppper(text[index+1])
    if cur == "":
        return False, False
    # next entries should be "Market Value"
    market_value, index = search_till_dot_before_cents(text, index+2, 3)
    market_value = concat_before_find(market_value, '.', 3)
    if not is_int(rem_char(market_value, ['.'])):
        return False, False
    market_value = float(market_value)
    # next entries should be "Book Cost"
    book_cost, index = search_till_dot_before_cents(text, index+1, 3)
    book_cost = concat_before_find(book_cost, '.', 3)
    if not is_int(rem_char(book_cost, ['.'])):
        return False, False
    book_cost = float(book_cost)
    ticker_row = pd.DataFrame({"date": [date],
                               "ticker": [ticker], 
                               "total_quantity": [total_quantity], 
                               "market_price": [market_price], 
                               "currency": [cur], 
                               "market_value": [market_value], 
                               "book_cost": [book_cost], 
                               })
    # found equity
    return True, ticker_row

# for finding activities
def found_activity(pdf_name, text, index, max_index, transaction_types):
    # for each type of transaction
    for transaction in transaction_types:
        pos_transaction = reduce_till_uppper(text[index])
        if pos_transaction != transaction:
            continue
        # found transaction
        # next entries should be "Charged"
        for j in range(index+1, max_index):
            # want to find an entry with a $
            if text[j].find("$") < 0:
                continue
            charge, _ = search_till_dot_before_cents(text, j, 3)
            charge = concat_before_find(charge, '.', 3)
            if not is_int(rem_char(charge, ['.'])):
                continue
            charge = float(charge)
            nindex = j
            break
        # if for loop was not broken
        else:
            continue
        # next entries should be "Credit"
        for j in range(nindex+1, max_index):
            # want to find an entry with a $
            if text[j].find("$") < 0:
                continue
            credit, _ = search_till_dot_before_cents(text, j, 3)
            credit = concat_before_find(credit, '.', 3)
            if not is_int(rem_char(credit, ['.'])):
                continue
            credit = float(credit)
            return True, [transaction, float(credit) - float(charge)]

        # failed to determine transaction information
        warn("Warning. PDF: {}. Could not determine charge or credit of type: {}"
             .format(pdf_name, transaction))
        user_response = u_confirm("Does the following contain a transaction of this "
                                  "type?{}\n".format(join_text_space(text, index-1, 
                                                                     index + 10)))
        if user_response == "y":
            charge = u_input("What is the 'Charged' value? ", float)
            credit = u_input("What is the 'Credit' value? ", float)
            return True, [transaction, float(credit) - float(charge)]
        elif user_response == "n":
            return False, False
        else:
            error_system_exit("Incorrect User Input: ({})".format(user_response))
    return False, False

# function to whether there are np.nan in data frame
def df_check(pdf_name, df, category):
    # grab the column headers of data frame
    cols = df.columns
    # iterate over columns
    for col in cols:
        if not np.isnan(df.at[0, col]):
            continue
        # nan was found
        warn("Warning. PDF: {}\nUnder {}, the item {} was not updated"
             .format(pdf_name, category, col))
        df.at[0, col] = u_input("Manually enter value: ", float)
    return df

def check_val(value_name, value, df, index, return_type):
    cor, nvalue = u_query("Is {} value: {} correct? ".format(value_name, value),
                         "What is {} value? ".format(value_name), return_type)
    if not cor:
        df.at[index, value_name] = nvalue
        return df, nvalue
    return df, value

def main(pdf_name, num_word_name):
    print("Processing: {}".format(pdf_name))
    # creating a pdf reader object 
    reader = PdfReader(pdf_name)

    # extract all text from pdf
    text = str()
    for page_index in range(len(reader.pages)):
        # getting a specific page from the pdf file 
        page = reader.pages[page_index] 
        # extracting text from page 
        text += page.extract_text() 
    # split based on spaces
    text = text.split()

    # start and end of current period
    statement_period = pd.DataFrame(columns = ["Start", "End"])

    # interested in the following information under "Cash Paid In" Section
    # Note "Cash" and "Portfolio" (i.e. "Total Portfolio") are not in "Cash Paid In" 
    # Section but are stated prior to "Cash Paid Out" Section and therefore included here
    cash_in = pd.DataFrame({"Cash": [np.nan], "Portfolio": [np.nan],
                            "Deposits": [np.nan], "Dividends": [np.nan]})

    # interested in the following bits of information under "Cash Paid Out" Section
    cash_out = pd.DataFrame({"Taxes": [np.nan], "Withdrawals": [np.nan]})     
    cursor_after_cash_out = 0

    # the range which portfolio equities should be found in
    cursor_equity_range = [len(text), len(text)]
    cursor_activity_range = [len(text), len(text)]

    # equities
    equities = pd.DataFrame(columns = ["date", "ticker", "total_quantity", "market_price", 
                                       "currency", "market_value", "book_cost"])

                                       #"region", "type", "sector"])
    # current period
    act_cur_period = pd.DataFrame({"DIV": [0], "CONT": [0], "DEP": [0], 
                                   "WD": [0], "NRT": [0]}, dtype = np.float64)

    #--------------- SCANNING DOCUMENT --------------- 
    # i is considered as cursor
    for i in range(len(text)):

        #--------------- ASSES WHERE CURSOR IS --------------- 
        # cursor has not reached "Cash Paid Out" section in "Portfolio Cash"
        if cursor_after_cash_out == 0:
            # we want to grab the first instance of "Fees" which occurs
            # directly after "Cash Paid Out" in "Portfolio Cash"
            if cursor_at_phrase(text, i, "Fees"):
                # note 'cursor_after_cash_out' is only updated once
                cursor_after_cash_out = 1
        # cursor has reached "Cash Paid Out" section in "Portfolio Cash"
        else:
            # have not determined beginning of "Portfolio Equities" section
            if cursor_equity_range[0] == len(text):
                # we want to grab the first instance of the "Portfolio Equities" section
                if cursor_at_phrase(text, i, "Portfolio Equities Symbol Total"):
                    # note 'cursor_equity_range[0]' is only updated once
                    cursor_equity_range[0] = i
            # previously found beginning of the "Portfolio Equities" section
            else:
                # have not determined beginning of "Activity - Current period" section
                if cursor_activity_range[0] == len(text):
                    # we want to grab the first instance of "Activity - Current period"
                    if (cursor_at_phrase(text, i, "Activity - Previous period(s)") or 
                        cursor_at_phrase(text, i, "Activity - Current period")):
                        # this defines the end of the "Portfolio Equities" section
                        # and the beginning of the "Activity - Current period" section
                        # note these are only updated once
                        cursor_equity_range[1] = i
                        cursor_activity_range[0] = i
                # previously found beginning of the "Activity - Current period" section
                else:
                    # have not determined end of "Activity - Current period" section
                    if cursor_activity_range[1] == len(text):
                        # want to grab first instance of the end of "Activity - Current 
                        # period" section
                        if cursor_at_phrase(text, i, "Transactions for Future "
                                                      "Settlement"):
                            # note this is updated only once
                            cursor_activity_range[1] = i
                        if cursor_at_phrase(text, i, "LEVERAGE DISCLOSURE"):
                            # note this is updated only once
                            cursor_activity_range[1] = i
        #--------------- ASSES WHERE CURSOR IS --------------- 

        #--------------- CURSOR PRIOR TO "CASH PAID OUT" --------------- 
        if cursor_after_cash_out == 0:
            # determine "Statement Period" dates
            if join_text_space(text, i, i+1)[-16:] == "Statement Period":
                # grab start and end dates
                start, end = found_date(pdf_name, text, i, num_word_name)
                # if successful, update the start and end dates of document
                statement_period = update_df_row(pdf_name, [start, end],
                                                 statement_period.columns, 
                                                 pd.DataFrame({"Start": [start], 
                                                               "End": [end]}),
                                                 statement_period)
            # check whether cursor is at any of the "Cash Paid In" items 
            found_item, item, item_val = found_cash_paid_item(text, i, cash_in)
            if found_item:
                # update cash_in
                cash_in = update_df_col_row(pdf_name, item, item_val, cash_in)
        #--------------- CURSOR PRIOR TO "CASH PAID OUT" --------------- 

        #--------------- CURSOR IN "CASH PAID OUT" --------------- 
        elif cursor_after_cash_out and i < cursor_equity_range[0]:
            # check whether cursor is at any of the "Cash Paid Out" items 
            found_item, item, item_val = found_cash_paid_item(text, i, cash_out)
            if found_item:
                # update cash_out
                cash_out = update_df_col_row(pdf_name, item, item_val, cash_out)
        #--------------- CURSOR IN "CASH PAID OUT" --------------- 

        #--------------- CURSOR IN "PORTFOLIO EQUITIES" --------------- 
        elif i >= cursor_equity_range[0] and i < cursor_activity_range[0]:
            # check whether cursor is at an equity
            equity, ticker_row = found_equity(text, i, statement_period.at[0, "End"])
            if equity:
                # update the entry of the equity
                equities = update_df_row(pdf_name, [text[i]], ["ticker"], ticker_row, 
                                         equities)
                equities.reset_index(drop = True, inplace = True)
        #--------------- CURSOR IN "PORTFOLIO EQUITIES" --------------- 

        #--------------- CURSOR IN "ACTIVITY - CURRENT PERIOD" --------------- 
        elif i >= cursor_activity_range[0] and i < cursor_activity_range[1]:
            # check whether cursor is at an activity
            activity, transaction = found_activity(pdf_name, text, i, 
                                                   cursor_activity_range[1],  
                                                   act_cur_period.columns)
            if activity:
                act_cur_period.at[0, transaction[0]] += transaction[1]
        #--------------- CURSOR IN "ACTIVITY - CURRENT PERIOD" --------------- 
    #--------------- SCANNING DOCUMENT --------------- 

    #--------------- ASSESSING RESULTS --------------- 
    # statement_period dates has been determined

    # cash_in and cash_out data check
    cash_in.rename(columns = {'Portfolio':'Total Portfolio'}, inplace = True) 
    df_check(pdf_name, cash_in, "Cash Paid In")
    df_check(pdf_name, cash_out, "Cash Paid Out")

    # equities
    equities_value = sum_round_by_two(equities["market_value"].values)
    cash = cash_in.at[0, "Cash"]
    total_port = cash_in.at[0, "Total Portfolio"]

    while (not within_one_cent(round(equities_value + cash, 2), round(total_port, 2))):
        # things did not add up
        warn("\n{} (Portfolio Equities) +\n{} (Cash)\n= {} != {} = Total Portfolio"
             .format(round(equities_value, 2), round(cash, 2),
                     round(equities_value + cash, 2), round(total_port, 2)))
        # check cash value
        cash_in, cash = check_val("Cash", cash, cash_in, 0, float)
        # check total portfolio value
        cash_in, total_port = check_val("Total Portfolio", total_port, cash_in, 0, float)
        user_response = u_confirm("Is Portfolio Equities value: {} correct?"
                                  .format(round(equities_value, 2)))
        if user_response == "y":
            print("It appears Wealth Simple made a mistake in summing up numbers")
            print("Proceeding with current data")
            break
        # check equities
        correct, num_missing = u_query("{}\nAre all portfolio equities identified?"
                                       .format(equities),
                                       "How many are missing? ", int)
        # there are missing equities
        if not correct:
            print("I am going to ask you to input the data from each missing equity\n")
            # for each missing equity
            for i in range(num_missing):
                print("Missing Equity {}:".format(i))
                equities = u_input_equity(pdf_name, equities, 
                                          statement_period.at[0, "End"], False, False)
                equities_value = sum_round_by_two(equities["market_value"].values)
        else:
            correct = u_query("Is there a ticker with incorrect data?", False, False)
            # update incorrect data
            if correct:
                index = u_input("Which ticker index?", int)
                equities = u_input_equity(pdf_name, equities, 
                                          statement_period.at[0, "End"], True, index)
                equities_value = sum_round_by_two(equities["market_value"].values)
            else:
                # failed to find issue
                proceed = u_confirm("Failed to find issue, proceed with data as is?")
                if proceed:
                    break
                else:
                    error_system_exit("Sorry, input data manually")
    # current period
    # dividends
    div_statement = round(cash_in.at[0, "Dividends"], 2) 
    div_summed = round(act_cur_period.at[0, "DIV"], 2)
    if div_statement != div_summed:
        warn("Dividend value in 'Cash Paid In' section is {}. This differs to that of "
             "summed dividends (DIV) = {} in 'Activity - Current period' section"
             .format(div_statement,div_summed))
        correct, div_statement = u_query("Is {} the correct Dividends value?"
                                         .format(div_statement),
                                         "Update Dividends value: ", float)
        if not correct:
            cash_in.at[0, "Dividends"] = div_statement
    # Taxes
    taxes = round(cash_out.at[0, "Taxes"], 2) 
    taxes_summed = -round(act_cur_period.at[0, "NRT"], 2)
    if taxes != taxes_summed:
        warn("Taxes value in 'Cash Paid Out' section is {}. This differs to that of "
             "summed taxes (NRT) = {} in 'Activity - Current period' section"
             .format(taxes, taxes_summed))
        correct, taxes = u_query("Is {} the correct Tax value?".format(taxes),
                                 "Update Tax value: ", float)
        if not correct:
            cash_out.at[0, "Taxes"] = taxes

    # deposits
    deposits = round(cash_in.at[0, "Deposits"], 2) 
    deposits_summed = round(act_cur_period.at[0, "CONT"], 2)
    deposits_summed += round(act_cur_period.at[0, "DEP"], 2)
    if deposits != deposits_summed:
        warn("Deposit value in 'Cash Paid In' section is {}. This differs to that of "
             "summed contributions (CONT/DEP) = {} in 'Activity - Current period' section"
             .format(deposits, deposits_summed))
        correct, deposits = u_query("Is {} the correct Deposit value?".format(deposits),
                                    "Update Depost value: ", float)
        if not correct:
            cash_in.at[0, "Deposits"] = deposits

    # withdrawals
    withdraw = round(cash_out.at[0, "Withdrawals"], 2) 
    withdraw_summed = round(act_cur_period.at[0, "WD"], 2)
    if withdraw != withdraw_summed:
        warn("Withdrawals value in 'Cash Paid out' section is {}. This differs to that of "
             "summed withdrawals (WD) = {} in 'Activity - Current period' section"
             .format(withdraw, withdraw_summed))
        correct, withdraw = u_query("Is {} the correct Withdrawal value?"
                                    .format(withdraw), "Update withdrawals value: ", float)
        if not correct:
            cash_in.at[0, "Withdrawals"] = withdraw
    #--------------- ASSESSING RESULTS --------------- 

    #--------------- OUTPUT STATEMENT DATA RESULTS --------------- 
    update_csv(statement_period, cash_in,"data/cash_paid_in.csv")

    update_csv(statement_period, cash_out,"data/cash_paid_out.csv")

    equities = check_info_equities(pdf_name, statement_period, equities)
    update_csv_equity(statement_period.at[0, "End"].strftime('%Y-%m-%d'), equities, 
                      "data/holdings.csv")
    #--------------- OUTPUT STATEMENT DATA RESULTS --------------- 

main(sys.argv[1], int(sys.argv[2]))
