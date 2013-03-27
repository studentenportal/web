// Error handling stuff

var raven_options = {
    logger: 'javascript',
    ignoreUrls: [],
    ignoreErrors: [],
    includePaths: [/https?:\/\/(www\.)?studentenportal\.ch/]
};
Raven.config('http://cbaa9dff64764fee963e7f71a0d7a898@sentry.studentenportal.ch/2', raven_options).install()

Dajaxice.setup({
    'default_exception_callback': function() {
        alert('Sorry, ein Fehler ist aufgetreten. Er wurde geloggt und ein Admin wurde benachrichtigt.');
        Raven.captureMessage('Unknown Dajaxice error', {tags: { key: "value" }})
    }
});


// Main stuff

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
