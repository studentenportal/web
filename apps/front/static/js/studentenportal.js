(function() {
    var navigation = responsiveNav(".nav-collapse", {
        customToggle: "#toggle"
    });
    Dajaxice.setup({
        'default_exception_callback': function() {
            alert('Sorry, ein Fehler ist aufgetreten. Er wurde geloggt und ein Admin wurde benachrichtigt.');
            Raven.captureMessage('Unknown Dajaxice error on page ' + window.location.pathname)
        }
    });
})();
