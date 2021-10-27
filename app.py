from re import S
from flask import Flask, json, render_template, redirect, url_for, session
from flask_wtf.csrf import CsrfProtect
import csv

from ProcessClaimsForm import ProcessClaimsForm
csrf = CsrfProtect()
import io

from UploadPaymentsForm import UploadPaymentsForm

from UploadPrivateKeysForm import UploadPrivateKeysForm

from flask_bootstrap import Bootstrap

from axie import AxiePaymentsManager, AxieClaimsManager

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
            stream = io.StringIO(form.file.data.stream.read().decode("UTF8"), newline=None)
            reader = csv.reader(stream)
            parsed_data = {}
            for row in reader:
                if len(row) != 2:
                    message = "Your CSV should have two columns"
                elif not row[0].startswith('ronin:'):
                    message = "Your address should start with ronin:"
                elif not row[1].startswith('0x'):
                    message = "Your private keys should start with 0x"
                if message != "":
                    return render_template('login.html', form=form, message=message)

                parsed_data[row[0]] = row[1]
            session['secrets'] = parsed_data
            return redirect(url_for('payments'))
        return render_template('login.html', form=form, message=message)

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SECRET_KEY'] = 'please-replace-this' # for wtf-forms

    Bootstrap(app)

    return app