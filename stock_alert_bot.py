import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yfinance as yf
import pandas as pd
import schedule
import time
import os
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

# Retrieve email credentials securely
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
MY_EMAIL_ADDRESS = os.getenv("MY_EMAIL_ADDRESS")

def get_stock_data(ticker):
    print(f"Fetching data for {ticker}...")  # Debugging statement
    stock = yf.Ticker(ticker)
    try:
        data = stock.history(period="2d")
        print(f"Fetched data for {ticker}: {data}")  # Debugging statement
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")  # Handle any errorss
        return None


def send_email_alert(stock, price, percentage):
    subject = f"ALERT: {stock} Stock Price Notification"
    body = f"ALERT: {stock} has reached a peak at ${price}! The percentage change is {percentage}%."
    
    
    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = EMAIL_ADDRESS
    message["To"] = MY_EMAIL_ADDRESS
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            text = message.as_string()
            server.sendmail(EMAIL_ADDRESS, MY_EMAIL_ADDRESS, text)
            print(f"Email sent successfully to {MY_EMAIL_ADDRESS}")
    except Exception as e:
        print(f"Error sending email: {e}")

def check_for_jump(ticker):
    
    data = get_stock_data(ticker)
    print(f"Checking stock: {ticker}") 
    if data is None:
        print(f"Skipping {ticker} due to no data.")  
        return 

    try:
        prev_close = data['Close'].iloc[0]
        current_price = data['Close'].iloc[1]
        percentage_change = ((current_price - prev_close) / prev_close) * 100

        print(f"Previous Close = ${prev_close}, Current Price = ${current_price}, Percentage Change = {percentage_change:.2f}%")

        if percentage_change >= 10:
            print(f"Triggering email alert for {ticker}...") 
            send_email_alert(ticker, current_price, round(percentage_change, 2))
        else:
            print(f"No significant change for {ticker}. No email sent.")
    
    except Exception as e:
        print(f"Error in check_for_jump: {e}")

        
# Schedules the task to check for jump every 1 minute
schedule.every(5).minutes.do(lambda: check_for_jump("GOOGL"))
print("Scheduled task registered.") 

print("Starting the script...") 
print("Checking scheduled tasks...") 

try:
    while True:
        schedule.run_pending()  
        time.sleep(1) 
except KeyboardInterrupt:
    print("Program interrupted by user. Exiting gracefully.")  

