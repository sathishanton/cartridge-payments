from decimal import Decimal

from django import forms
from mezzanine.conf import settings

from payments.multipayments.forms import base
from payments.multipayments import const
from hashlib import sha512
from django.conf import settings
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger('django')
logger.info("##################hello PAYU######################")

KEYS = ('key', 'txnid', 'amount', 'productinfo', 'firstname', 'email',
        'udf1', 'udf2', 'udf3', 'udf4', 'udf5',  'udf6',  'udf7', 'udf8',
        'udf9',  'udf10')


class PayUSubmissionForm(base.ExternalPaymentForm):

    #payu specific fields
    key = forms.CharField(required=False, widget=forms.HiddenInput())
    hash = forms.CharField(required=False, widget=forms.HiddenInput())

    # cart order related fields
    txnid = forms.CharField(required=False, widget=forms.HiddenInput())
    productinfo = forms.CharField(required=False, widget=forms.HiddenInput())
    amount = forms.DecimalField(decimal_places=2, widget=forms.HiddenInput())

    # buyer details
    firstname = forms.CharField(required=False, widget=forms.HiddenInput())
    lastname = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(required=False, widget=forms.HiddenInput())
    phone = forms.RegexField(regex=r'\d{10}', min_length=10, max_length=10,widget=forms.HiddenInput())
    address1 = forms.CharField(required=False, widget=forms.HiddenInput())
    address2 = forms.CharField(required=False, widget=forms.HiddenInput())
    city = forms.CharField(required=False, widget=forms.HiddenInput())
    state = forms.CharField(required=False, widget=forms.HiddenInput())
    country = forms.CharField(required=False, widget=forms.HiddenInput())
    zipcode = forms.CharField(required=False, widget=forms.HiddenInput())
    
    # merchant's side related fields
    furl = forms.URLField(required=False, widget=forms.HiddenInput())
    surl = forms.URLField(required=False, widget=forms.HiddenInput())
    curl = forms.URLField(required=False, widget=forms.HiddenInput())
    codurl = forms.URLField(required=False, widget=forms.HiddenInput())
    touturl = forms.URLField(required=False, widget=forms.HiddenInput())
    udf1 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf2 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf3 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf4 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf5 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf6 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf7 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf8 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf9 = forms.CharField(required=False, widget=forms.HiddenInput())
    udf10 = forms.CharField(required=False, widget=forms.HiddenInput())
    pg = forms.CharField(required=False, widget=forms.HiddenInput())
    drop_category = forms.CharField(required=False, widget=forms.HiddenInput())
    custom_note = forms.CharField(required=False, widget=forms.HiddenInput())
    note_category = forms.CharField(required=False, widget=forms.HiddenInput())
    service_provider = forms.CharField(required=False, widget=forms.HiddenInput())
    


    def __init__(self, request, order_form, *args, **kwargs):

        super(PayUSubmissionForm, self).__init__(*args, **kwargs)
        cart = request.cart
        self.order = self.get_or_create_order(request, order_form)
        form_value = lambda name, default: request.POST.get(\
                        'shipping_detail_%s' % name, default)

        shipping_type = request.session.get("shipping_type")
        shipping_total = request.session.get("shipping_total")

        tax_type = request.session.get("tax_type")
        tax_total = request.session.get("tax_total")

        cart_price = cart.total_price()
        ship_price = Decimal(str(shipping_total)).quantize(const.NEAREST_CENT)
        tax_price = Decimal(str(tax_total)).quantize(const.NEAREST_CENT)
        total_price = cart_price + \
            (ship_price if ship_price else Decimal('0')) + \
            (tax_price if tax_price else const.Decimal('0'))
        try:
            s_key = request.session.session_key
        except:
            # for Django 1.4 and above
            s_key = request.session._session_key
        
        #payu = get_backend_settings('payu')
        #payu specific fields
        pkey = settings.PAYU_MERCHANT_KEY
        self.fields['key'].initial = settings.PAYU_MERCHANT_KEY
    
        # cart order related fields
        ptxid = self.order.callback_uuid
        self.fields['txnid'].initial = self.order.callback_uuid
        pprice = str(total_price)
        self.fields['amount'].initial = total_price
        self.fields['productinfo'].initial = "Test Products"
       
        # buyer details
        pfirstname = self.order.billing_detail_first_name
        self.fields['firstname'].initial = pfirstname
        pemail = self.order.billing_detail_email
        self.fields['email'].initial = pemail

        # merchant's side related fields
        self.fields['surl'].initial = self.lambda_reverse(\
            settings.PAYU_SRETURN_URL, cart, self.order.callback_uuid, \
            order_form)
        self.fields['furl'].initial = self.lambda_reverse(\
            settings.PAYU_FRETURN_URL, cart, self.order.callback_uuid, \
            order_form)
        
        self.fields['udf1'].initial = ""
        self.fields['udf2'].initial = "SSA"
        self.fields['udf3'].initial = ""
        self.fields['udf4'].initial = "15"
        self.fields['udf5'].initial = ""
        self.fields['udf6'].initial = ""
        self.fields['udf7'].initial = ""
        self.fields['udf8'].initial = ""
        self.fields['udf9'].initial = ""
        self.fields['udf10'].initial = ""
        
    

        hashp = sha512(pkey.encode('utf-8'))
        hashp.update("|".encode('utf-8'))        
        hashp.update(ptxid.encode('utf-8'))
        hashp.update("|".encode('utf-8'))
        hashp.update(pprice.encode('utf-8'))
        hashp.update("|".encode('utf-8'))
        hashp.update("Test Products".encode('utf-8'))
        hashp.update("|".encode('utf-8'))
        hashp.update(pfirstname.encode('utf-8'))
        hashp.update("|".encode('utf-8'))
        hashp.update(pemail.encode('utf-8'))
        hashp.update("|".encode('utf-8'))
        hashp.update("".encode('utf-8')) #udf1
        hashp.update("|".encode('utf-8'))
        hashp.update("SSA".encode('utf-8')) #udf2
        hashp.update("|".encode('utf-8'))
        hashp.update("".encode('utf-8')) #udf3
        hashp.update("|".encode('utf-8'))
        hashp.update("15".encode('utf-8')) #udf4
        hashp.update("|".encode('utf-8'))
        hashp.update("".encode('utf-8')) #udf5
        hashp.update("|".encode('utf-8'))
        hashp.update("".encode('utf-8')) #udf6
        hashp.update("|".encode('utf-8'))
        hashp.update("".encode('utf-8')) #udf7
        hashp.update("|".encode('utf-8'))
        hashp.update("".encode('utf-8')) #udf8
        hashp.update("|".encode('utf-8'))
        hashp.update("".encode('utf-8')) #udf9
        hashp.update("|".encode('utf-8'))
        hashp.update("".encode('utf-8')) #udf10
        hashp.update("|".encode('utf-8'))
        psalt=settings.PAYU_MERCHANT_SALT
        hashp.update(psalt.encode('utf-8'))
        self.fields['hash'].initial = hashp.hexdigest().lower()

        i = 1
        if cart.has_items():
            for item in cart.items.all():
                rounded = item.unit_price.quantize(const.NEAREST_CENT)
                qty = int(item.quantity)
                self.add_line_item(i, item.description, rounded, qty)
                i += 1

        # Add shipping as a line item
        if shipping_type and shipping_total:
            self.add_line_item(i, shipping_type, shipping_total, 1)
            i += 1

        # Add tax as a line item
        if tax_type and tax_total:
            self.add_line_item(i, tax_type, tax_total, 1)
            i += 1


    def add_line_item(self, number, name, amount, quantity):
        # FIELDS
        self.fields['item_name_%d' % number] = self._hidden_charfield()
        self.fields['amount_%d' % number] = self._hidden_charfield()
        self.fields['quantity_%d' % number] = self._hidden_charfield()
        # VALUES
        self.fields['item_name_%d' % number].initial = name
        self.fields['amount_%d' % number].initial = amount
        self.fields['quantity_%d' % number].initial = quantity

    def _hidden_charfield(self):
        return forms.CharField(widget=forms.HiddenInput())

    @property
    def action(self):
        return settings.PAYU_SUBMIT_URL
