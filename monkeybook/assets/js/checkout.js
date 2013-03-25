var orderTotal;

function updateTaxAndTotal() {
    var fullQty = $('#fullQty').val() ? parseInt($('#fullQty').val()) : 0;
    var abridgedQty = $('#abridgedQty').val() ? parseInt($('#abridgedQty').val()) : 0;
    var digitalQty = $('#id_digital_upgrade').val() ? parseInt($('#id_digital_upgrade').val()) : 0;

    $('#fullTotal').text((fullQty * fullPrice).toFixed(2));
    $('#abridgedTotal').text((abridgedQty * abridgedPrice).toFixed(2));

    var untaxedSubtotal = digitalQty * digitalPrice;
    var taxedSubtotal = fullQty * fullPrice + abridgedQty * abridgedPrice;

    var isShipping = (fullQty > 0) || (abridgedQty > 0);
    var shippingSubtotal = 0;
    if (isShipping)
        shippingSubtotal = shippingPrice;

    var isTax = false;
    if (diffShipping() && shipping_is_us() && ($('#id_shipping_us_state').val() == 'CA')) {
        isTax = true;
    } else if (billing_is_us() && $('#id_billing_us_state').val() == 'CA') {
        isTax = true;
    }
    var taxSubtotal = 0;
    if (isTax) {
        taxSubtotal = taxedSubtotal * caTaxRate;
        $('#taxTotal').text(taxSubtotal.toFixed(2));
        // Show the tax subtotal
        $('.taxSubtotalDiv').show();
    }

    orderTotal = untaxedSubtotal + taxedSubtotal + shippingSubtotal + taxSubtotal;
    $('#orderTotal').text(orderTotal.toFixed(2));
}

function onQtyChanged() {
    updateTaxAndTotal();

    $('#id_full_quantity').val($('#id_fullQty').val());
    $('#id_abridged_quantity').val($('#id_abridgedQty').val());
}

function billing_is_us() {
    return $('#id_billing_country').val() == 'US';
}

function shipping_is_us() {
    return $('#id_shipping_country').val() == 'US';
}

function diffShipping() {
    return $('.sameShipping:checked').val() == 'diff';
}

function updateState() {
    if ((diffShipping() && shipping_is_us() && $('#id_shipping_us_state').val() == 'CA') ||
        (!diffShipping() && billing_is_us() && $('#id_billing_us_state').val() == 'CA')) {
        $('.taxSubtotalDiv').slideDown(400);
    } else {
        // No sales tax
        $('.taxSubtotalDiv').slideUp(400);
    }
    updateTaxAndTotal();
}

$(document).ready(function() {
    $('.qtySelect').change(onQtyChanged);
    // Select the United States by default
    $('option[value="US"]').attr('selected', 'selected');
    $('.usStateDiv option[value="CA"]').attr('selected', 'selected');
    $('.countrySelect').change(function(){
        var el = $(this);
        var fieldset = el.parents('fieldset');
        if (el.val() == 'US') {
            fieldset.find('.nonUsStateDiv').hide();
            fieldset.find('.usStateDiv').show();
        } else {
            fieldset.find('.usStateDiv').hide();
            fieldset.find('.nonUsStateDiv').show();
        }
        updateState();
    });
    $('.usStateSelect').change(updateState);
    $('.sameShipping').change(function(){
        if (diffShipping()) {
            $('.shippingForm').slideDown(800);
        } else {
            $('.shippingForm').slideUp(800);
        }
    });

    $.validator.addMethod("zipcode", function(value, element) {
        var val = $.trim(value);
        return this.optional(element) || (/^\d{5}$/.test(val) || /^\d{9}$/.test(val) || /^\d{5}-\d{4}$/.test(val) || /^\d{5} \d{4}$/.test(val))
    }, "Please enter a correct ZIP code");

    $.validator.addMethod("cvccode", function(value, element) {
        return Stripe.validateCVC(value);
    }, "Please enter a valid security code");

    $('#orderForm').submit(function(e){
//        $('.submitButton').hide();
//        $('.processingButton').show();

        $('#orderForm').validate({
            debug: true,
            errorElement: "span",
            errorClass: "help-inline",
            onfocusout: false,
            onkeyup: false,
            groups: {
                expiration: "exp_month exp_year"
            }, rules: {
                billing_us_state: {        required: { depends: billing_is_us }},
                billing_us_zip: {          required: { depends: billing_is_us }},
                billing_state_province: {  required: { depends: function(el) { return !billing_is_us(); }}},
                billing_postal: {        required: { depends: function(el) { return !billing_is_us(); }}},

                shipping_address: {        required: { depends: diffShipping }},
                shipping_city: {           required: { depends: diffShipping }},
                shipping_us_state: {       required: { depends: function(el) { return diffShipping() && shipping_is_us(); }}},
                shipping_us_zip: {         required: { depends: function(el) { return diffShipping() && shipping_is_us(); }}},
                shipping_state_province: { required: { depends: function(el) { return diffShipping() && !shipping_is_us(); }}},
                shipping_postal: {       required: { depends: function(el) { return diffShipping() && !shipping_is_us(); }}},

                exp_month: { min: 1, max: 12 },
                exp_year: { min: 13, max: 20 }

            }, messages: {
                exp_month: {
                    min: "Please enter a month of 1 or greater",
                    max: "Please enter a month of 12 or less"
                }, exp_year: {
                    min: "Please enter a year of 13 or greater",
                    max: "Please enter a year of 20 or less"
                }
            }, showErrors: function(errorMap, errorList) {
                $('.control-group').removeClass('error');
                // Add .error to each parent control-group
                _.each(errorList, function(error){
                    $(error.element).parents('.control-group').addClass('error');
                });
                this.defaultShowErrors();

            }, errorPlacement: function(error, element) {
                if (element.attr("name") == "exp_month"
                    || element.attr("name") == "exp_year" )
                    error.insertAfter("#id_exp_year");
                else
                    error.insertAfter(element);

            }, submitHandler: function(form) {
                Stripe.createToken({
                    number: $('#id_card_number').val(),
                    cvc: $('#id_cvv_code').val(),
                    exp_month: $('#id_exp_month').val(),
                    exp_year: $('#id_exp_year').val(),
                    name: $('#id_name_on_card').val(),
                    address_line1: $('#id_billing_address').val(),
                    address_line2: $('#id_billing_address2').val(),
                    address_city: $('#id_billing_city').val(),
                    address_state: shipping_is_us() ? $('#id_billing_us_state').val() : $('#id_billing_state_province').val(),
                    address_zip: shipping_is_us() ? $('#id_billing_us_zip').val() : $('#id_billing_postal').val(),
                    address_country: $('#id_billing_country').val()
                }, onStripeResponse);

            }, invalidHandler: function(form, validator) {
                $('.submitButton').show();
                $('.processingButton').hide();
            }
        });

        e.preventDefault();
        return false;
    });
});

function onStripeResponse(status, response) {
    if (response.error) {
        $('.paymentFormError').text(response.error.message);
        $('.paymentForm .control-group').addClass('error');

        $('.submitButton').show();
        $('.processingButton').hide();
    } else {
        // "tok_14KZQbThChozhQ"
        $('#id_stripe_single_use_token').val(response['id']);
        $('#id_charged_total').val(parseFloat($('#orderTotal').text()));

        // Remove the payment fields so they don't cross the wire
        $('#id_card_number').val("");
        $('#id_cvv_code').val("");
        $('#id_exp_month').val("");
        $('#id_exp_year').val("");
        $('#id_name_on_card').val("");

        // POST the form back to the view
        $('#orderForm').off('submit');
        $('#orderForm').submit();
    }
}
