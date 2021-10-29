# Axie Payment Automation

## Running the app (non-devs)

The project can be run as a web app or as an electron app.
[Download the electron app here](download)
Or, you can access the same UI via the web: [visit site](visit)

## For developers

The app is a flask app that simply wraps the functionality and makes some small adjustments to [axie-scholar-utils.](https://github.com/FerranMarin/axie-scholar-utilities/tree/main/axie-scholar-utilities)

### Steps to run as web app

```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
flask run
```

### Steps to run as electron app:

```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
npm install
pyinstaller manage.py
electron .
```

## Monetization

Right now, I just put in a 1% fee for the payment hardcoded into the app. I feel bad about this though because a lot of the credit should go to the original author of the axie-scholar-utilities. So if you have a better idea of how to monetize, feel free to open a PR or shoot me a message (find me by going to my [linkchain](https://linkchain.me/michael))
