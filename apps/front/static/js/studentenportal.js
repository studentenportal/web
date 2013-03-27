$(document).ready(function() {
    // Enable dropdowns
    $('.dropdown-toggle').dropdown()

    // Enable datepickers
    options = {
        dateFormat: 'dd.mm.yy',
        showAnim: 'fadeIn',
    };
    $('#id_start_date').datepicker(options);
    $('#id_end_date').datepicker(options);
});

Dajaxice.setup({
    'default_exception_callback': function() {
        alert('Sorry, ein Fehler ist aufgetreten. Er wurde geloggt und ein Admin wurde benachrichtigt.');
        Raven.captureMessage('Unknown Dajaxice error on page ' + window.location.pathname)
    }
});
