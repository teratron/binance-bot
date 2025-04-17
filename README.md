# Binance Trading Bot with QQE Indicator

This is a trading bot for Binance that uses the QQE (Quantitative Qualitative Estimation) indicator and other technical analysis tools to make trading decisions.

## Features

- Uses the official Binance Connector package for API interactions
- Implements QQE and other technical indicators using TA-Lib
- Secure API key management with python-dotenv-vault
- Comprehensive logging system
- Code quality maintained with ruff
- Package management with UV

## Setup

### Prerequisites

- Python 3.11+
- UV package manager
- TA-Lib (requires separate installation of C library)

### Installation

1. Clone this repository
2. Install dependencies using UV (no requirements.txt needed):
3. Create a `.env` file with your Binance API credentials:

```shell
# Run the installation script
install_with_uv.bat
```

```env
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

## Usage

Run the bot with:

```shell
python main.py
```

## Configuration

Edit the `config.py` file to adjust trading parameters, including:

- Trading pairs
- QQE indicator settings
- Risk management parameters
- Trading strategy options

## Disclaimer

This bot is for educational purposes only. Use at your own risk. Cryptocurrency trading involves significant risk and you should never invest money you cannot afford to lose.

<https://binance-connector.readthedocs.io>

<https://github.com/binance/binance-connector-python/blob/master/examples/>

<https://www.youtube.com/watch?v=AV1boDD-uWc>

<https://www.youtube.com/watch?v=NaWH3zH_SNw&t=113s>

<https://www.youtube.com/watch?v=kZ6wfxVyk2w>

<https://www.youtube.com/watch?v=UYtFByS6tCs>

<https://www.youtube.com/watch?v=EeT3Ore4Sao&list=PLvzuUVysUFOuB1kJQ3S2G-nB7_nHhD7Ay&index=10>

<https://www.youtube.com/watch?v=gMRee2srpe8>

## Examples

<https://github.com/cromewar/Binance-trading-bot>

<https://github.com/hackingthemarkets/binance-tutorials>

<https://github.com/hackingthemarkets/tradingview-binance-strategy-alert-webhook>

## Numpy

<https://www.youtube.com/watch?v=Dh0cdMlcrbU>

## Pandas

<https://www.youtube.com/watch?v=cEeY0opsVMw>

## Matplotlib

<https://www.youtube.com/watch?v=RAXDcUrFD2o>

## TA-Lib

<https://ta-lib.github.io/ta-lib-python/install.html>

## Helpers

<https://www.unixtimestamp.com/>
