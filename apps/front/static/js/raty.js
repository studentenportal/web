$.fn.raty.defaults.path = '/static/img/raty/';
$.fn.raty.defaults.number = 10;
$.fn.raty.defaults.hintList = [1,2,3,4,5,6,7,8,9,10]

function submitScore(category) {
    return function(score, evt) {
        url = document.URL + 'rate/';
        $.ajax({
            type: 'POST',
            url: url,
            data: {'score': score, 'category': category},
            success: function(data, textStatus, jqXHR) {
                $('#lrating-' + category + '-val').text(score);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // Couldn't complete ajax request.
                // Reset raty and show error message.
                alert(errorThrown + ': ' + jqXHR.responseText);
                $('#lrating-' + category).raty('cancel');
            },
        });
    }
}

$(document).ready(function() {
    $('#lrating-d').raty({
        starHalf: 'star-half-red.png',
        starOff: 'star-off-red.png',
        starOn: 'star-on-red.png',
        click: submitScore('d'),
        start: function() {
            return $(this).attr('data-rating');
        }
    });
    $('#lrating-m').raty({
        starHalf: 'star-half-green.png',
        starOff: 'star-off-green.png',
        starOn: 'star-on-green.png',
        click: submitScore('m'),
        start: function() {
            return $(this).attr('data-rating');
        }
    });
    $('#lrating-f').raty({
        starHalf: 'star-half-blue.png',
        starOff: 'star-off-blue.png',
        starOn: 'star-on-blue.png',
        click: submitScore('f'),
        start: function() {
            return $(this).attr('data-rating');
        }
    });
});
