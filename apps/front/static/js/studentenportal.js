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
