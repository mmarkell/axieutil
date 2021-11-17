
import logging
from re import S
from flask import Flask, flash, json, render_template, redirect, url_for, session
from flask_wtf.csrf import CsrfProtect
import requests

from requests.adapters import RetryError

from ProcessClaimsForm import ProcessClaimsForm
csrf = CsrfProtect()
import io

from UploadPaymentsForm import UploadPaymentsForm

from UploadPrivateKeysForm import UploadPrivateKeysForm

from flask_bootstrap import Bootstrap

from axie import AxiePaymentsManager, AxieClaimsManager
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from flask_session import Session

from datetime import timedelta

def has_unclaimed_slp(acc):
    url = f"https://game-api.skymavis.com/game-api/clients/{acc}/items/1"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36"})
    except RetryError:
        logging.critical(f"Failed to check if there is unclaimed SLP for acc {acc}")
        return False
    if 200 <= response.status_code <= 299:
        return int(response.json()['total'])
    return False

def secretsFromMnemonics(seedPhrase):
    # Initialize Ethereum mainnet BIP44HDWallet
    bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
    # Get Ethereum BIP44HDWallet from mnemonic
    bip44_hdwallet.from_mnemonic(mnemonic=seedPhrase)
    # Clean default BIP44 derivation indexes/paths
    bip44_hdwallet.clean_derivation()
    output = {}

    # Get Ethereum BIP44HDWallet information's from address index
    for i in range(10):
        # Derivation from Ethereum BIP44 derivation path
        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=EthereumMainnet, account=0, change=False, address=i
        )
        # Drive Ethereum BIP44HDWallet
        bip44_hdwallet.from_path(path=bip44_derivation)

        if has_unclaimed_slp(bip44_hdwallet.address()):
            output[bip44_hdwallet.address().replace('0x', 'ronin:')] = '0x' + bip44_hdwallet.private_key()
            # Print address_index, path, address and private_key
        # Clean derivation indexes/paths
        bip44_hdwallet.clean_derivation()
    return output

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

def create_app():
    app = Flask(__name__)
    csrf.init_app(app)

    @app.route('/claim/', methods=['GET', 'POST'])
    def claim():
        form = ProcessClaimsForm()
        
        secrets = session['secrets']
        payment_percents = session['payment_percents']
        message = False
        if form.validate_on_submit():
            message = False
            if not secrets or not payment_percents:
                return render_template('claims.html', form=form, payment_percents=payment_percents, secrets=secrets)
            
            paid_scholars_amount = 0
            claimed_amount = 0
            apm = AxiePaymentsManager(payment_percents, secrets, auto=True)
            acm = AxieClaimsManager(payment_percents, secrets)
            try:
                apm.verify_inputs()
                apm.prepare_payout()
                
                summary = apm.summary
                paid_scholars_amount = summary.scholar["slp"]

                acm.verify_inputs()
                claimed_amount = acm.prepare_claims()
            except BaseException as err:
                message = str(err)
            return render_template('complete.html', paid_scholars_amount=paid_scholars_amount, claimed_amount=claimed_amount, message=message)
        return render_template('claims.html', form=form, payment_percents=payment_percents, secrets=secrets)

    @app.route('/payments/', methods=['GET', 'POST'])
    def payments():
        secrets = session['secrets']
        form = UploadPaymentsForm()
        message = ""
        if form.validate_on_submit():

            message = ""
            jsonData = io.StringIO(form.file.data.stream.read().decode("UTF8"), newline=None).read()

            if not validateJSON(jsonData):
                message = "Please input valid JSON"

            if message: # handle error case
                return render_template('payments.html', secrets=secrets, form=form, message=message)

            payment_percents = json.loads(jsonData)
            if payment_percents is None:
                message = "Please upload a file"
            session['payment_percents'] = payment_percents
            return redirect(url_for('claim'))
        return render_template('payments.html', secrets=secrets, form=form, message=message)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = UploadPrivateKeysForm()
        message = ""
        if form.validate_on_submit():
            message = ""
            try:
                flash('This may take a while')
                secrets = secretsFromMnemonics(form.seed_phrase.data)
                print('adding secrets', secrets)
                session['secrets'] = secrets
                return redirect(url_for('payments'))
            except Exception as err:
                message = str(err)
                return render_template('login.html', form=form, message=message)
        return render_template('login.html', form=form, message=message)

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
    app.config['SESSION_FILE_THRESHOLD'] = 1
    app.config['SECRET_KEY'] = 'please-replace-this' # for wtf-forms

    Bootstrap(app)

    sess = Session()
    sess.init_app(app)

    return app

app = create_app()