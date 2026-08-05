import yfinance as yf
data = yf.download("MSFT", start="2025-10-20", end="2025-11-10", progress=False)
print(data)