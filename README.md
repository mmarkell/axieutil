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
