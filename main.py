import requests
import datetime
import constants
# API key
key = 'KEY LEFT OUT'



def get_price_history(**kwargs):
    # Method/function to call to website and upload parameters and return results
    # **kwargs means it can handle many arguments that are defined by a keyword in which the method can handle

    # URL address for API, pulling 'symbol' key from kwargs
    url = 'https://api.tdameritrade.com/v1/marketdata/{}/pricehistory'.format(kwargs.get('symbol'))

    # Initialize dictionary
    user_params = {}
    # Add 'apikey' to "user_params" dictionary
    user_params.update({'apikey': key})

    # for every argument ("arg") in kwargs, add it to the "user_params" dictionary
    for arg in kwargs:
        user_params.update({arg: kwargs.get(arg)})

    # Return the results by sending "url" and the supplied "params" (params is a keyword on the API), json is the format it is being received in
    return requests.get(url, params=user_params).json()


def get_over_under(short_list, long_list, short_length, long_length):
    over_under = []
    for i in range(len(short_list)):
        if i < long_length:
            over_under.append(constants.NA)
        elif short_list[i] > long_list[i]:
            over_under.append(constants.OVER)
        elif short_list[i] < long_list[i]:
            over_under.append(constants.UNDER)
        else:
            over_under.append(constants.EQUALS)
    return over_under





def sma(lookback_length, actual_close_list): # return list with SMA values
    sma_list = []  # initialize sma list

    # add 0 to the list for the first areas where SMA can't be calculated
    for i in range(lookback_length-1):
        sma_list.append(0)

    # calculate SMA and store in list
    for i in range(lookback_length-1, len(actual_close_list)):
        sma_avg = 0  # for calculating SMA
        for j in range(i-(lookback_length-1), i+1):
            sma_avg = sma_avg + actual_close_list[j]
        sma_list.append(sma_avg / lookback_length)

    return sma_list


def ema(lookback_length, actual_close_list): # return list with EMA values
    """
    EMA calculation:
    EMA = Price(t) * k + EMA(y) * (1-k)
    t = today
    y = yesterday
    k = "weight" = 2 / (n + 1)
    n = lookback length
    """

    ema_list = []  # initialize ema list

    # add 0 to the list for the first areas where EMA can't be calculated
    for i in range(lookback_length-1):
        ema_list.append(0)

    # calculate EMA and store in list
    for i in range(lookback_length-1, len(actual_close_list)):

        if i == lookback_length - 1:  # calculate first EMA to be SMA
            sma_avg = 0  # for calculating EMA first entry (which is SMA)
            for j in range(i - (lookback_length - 1), i + 1):
                sma_avg = sma_avg + actual_close_list[j]
            ema_list.append(sma_avg / lookback_length)
        else:  # calculate EMA for all other values after the first
            # define variables for formula

            current_price = actual_close_list[i]
            prior_ema = ema_list[len(ema_list) - 1]
            weighted_variable = 2 / (lookback_length + 1)
            # calculate EMA

            current_ema = (current_price * weighted_variable + prior_ema * (1 - weighted_variable))
            ema_list.append(current_ema)

    return ema_list

def get_dates(data_API_dictionary):
    # separate & return the dates formatted from the dictionary in local time zone

    dates = []  # initialize date list

    # calculate timezone difference
    current_datetime = round(datetime.datetime.timestamp(datetime.datetime.now()))
    utc_datetime = round(datetime.datetime.timestamp(datetime.datetime.utcnow()))
    time_difference = utc_datetime - current_datetime

    # loop to separate & return the dates formatted from the dictionary in local time zone
    for i in range(len(data_API_dictionary['candles'])):
        # format date... requires //1000 & adding 2 hours (+7200)... %a is Day, %b is Month, %d is numeric date
        dates.append(datetime.date.fromtimestamp(data_API_dictionary['candles'][i]['datetime'] // 1000 + time_difference).strftime('%a, %b %d %Y'))
    return dates


def get_closes(data_API_dictionary):
    # separate & return the dates formatted from the dictionary
    closes = []
    for i in range(len(data_API_dictionary['candles'])):
        closes.append(float(data_API_dictionary['candles'][i]['close']))
    return closes



# initialize data & variables
short_length = 9
long_length = 20
one_year_ms = 31556952000  # 1 year in milliseconds

#calculate end date and start date (set to today & one year ago)
end_date = round(datetime.datetime.timestamp(datetime.datetime.now())*1000)
start_date = end_date - one_year_ms - one_year_ms

# call API with criteria
data_from_API = get_price_history(symbol='AAPL', period=1,  periodType='year', frequency=1, frequencyType='daily',
                                  needExtendedHoursData='false', startDate=start_date, endDate=end_date)

# pull dates & close from API data, calculate SMAs & EMAs
dates = get_dates(data_from_API)
closes = get_closes(data_from_API)
long_ma = sma(long_length, closes)
short_ma = ema(short_length, closes)
over_under = get_over_under(short_ma, long_ma, short_length, long_length)

#loop print
for i in range(len(dates)):
    print(f"Date: {dates[i]} =", f"Close: {round(closes[i], 2):>7.2f},",
          f"Short-EMA: {round(short_ma[i], 2):>7.2f},", f"Long-SMA: {round(long_ma[i], 2):>7.2f}", end=' ')
    if i == 0:
        print("")
    else:
        if over_under[i] == over_under[i-1] or over_under[i-1] == constants.NA:
            print("")
        else:
            print("-", over_under[i])










