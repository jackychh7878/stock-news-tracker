import requests
from datetime import datetime, timedelta
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

delta_change = 0
NEWS_ENDPOINT = "https://newsapi.org/v2/everything?"
STOCK_ENDPOINT = "https://www.alphavantage.co/query?"

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
def check_delta():
    parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": MY_KEY
    }
    response = requests.get(STOCK_ENDPOINT, params=parameters)
    response.raise_for_status()
    data = response.json()

    yesterday = datetime.now() - timedelta(2)
    day_before = datetime.now() - timedelta(3)

    yesterday_high = data["Time Series (Daily)"][yesterday.strftime("%Y-%m-%d")]['2. high']
    day_before_low = data["Time Series (Daily)"][day_before.strftime("%Y-%m-%d")]['3. low']
    percentage_change = (float(yesterday_high) - float(day_before_low)) / float(day_before_low)

    global delta_change
    delta_change = round(percentage_change,3)
    if abs(percentage_change) > 0.05:
        return True
    else:
        return False

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 
def get_news():
    yesterday = datetime.now() - timedelta(2)
    parameters = {
        "q": COMPANY_NAME,
        "from": yesterday,
        "sortby": "popularity",
        "apikey": MY_KEY_NEWS
    }
    response = requests.get(NEWS_ENDPOINT, params=parameters)
    response.raise_for_status()
    data = response.json()
    global delta_change

    article = ""
    # for i in range(3):
    #     article += f"""
    # {STOCK}: {"🔺" if delta_change > 0  else "🔻"} {abs(delta_change)*100}%
    # Headline: {data["articles"][i]["title"]}
    # Brief: {data["articles"][i]["description"]}
    # """
    new_list = data["articles"][:3]
    for item in new_list:
        article += f"""
            {STOCK}: {"🔺" if delta_change > 0 else "🔻"} {abs(delta_change) * 100}%
            Headline: {item["title"]}
            Brief: {item["description"]}
        """
    return article

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 
if check_delta():
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body= get_news(),
        from_=FROM_NUMBER,
        to=TO_NUMBER
    )
    print(message.status)

# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
