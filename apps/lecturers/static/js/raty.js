$.fn.raty.defaults.path = '/static/img/raty/';
$.fn.raty.defaults.number = 10;
$.fn.raty.defaults.hintList = [1,2,3,4,5,6,7,8,9,10]

function submitScore(category) {
    return function(score, evt) {
        var lecturer_pk = $('h1.lecturer-name').attr('data-lecturer-pk');
        Dajaxice.apps.lecturers.rate_lecturer(
            lecturerRatingCallback, {
                'lecturer_pk': lecturer_pk, 'category': category, 'score': score
            }
        );
    }
}

function lecturerRatingCallback(data) {
    $('.lrating-' + data.category + '-avg').text(data.rating_avg);
    var rating_count_text = data.rating_count == 1 ? ' Bewertung' : ' Bewertungen';
    $('.lrating-' + data.category + '-avg').attr('title', data.rating_count + rating_count_text);
}

$(document).ready(function() {

    // Lecturer ratings
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


    // Document ratings
    $('.drating').raty({
        noRatedMsg: 'Du kannst deine eigenen Uploads nicht bewerten.',
        click: function(score, evt) {
            var rating_div = $(this);
            var url = rating_div.attr('data-url');
            var summary_url = rating_div.attr('data-summary-url')
            $.ajax({
                type: 'POST',
                url: url,
                data: {'score': score},
                error: function(jqXHR, textStatus, errorThrown) {
                    // Couldn't complete ajax request.
                    // Reset raty and show error message.
                    alert(errorThrown + ': ' + jqXHR.responseText);
                    rating_div.raty('cancel');
                },
                success: function(data, textStatus, jqXHR) {
                    // Update average rating etc...
                    var summary_span = rating_div.siblings('.rating_summary')
                    summary_span.load(summary_url)
                }
            });
        },
        start: function() {
            return $(this).attr('data-rating');
        }
    });
    $('.drating').each(function() {
        if ($(this).attr('data-readonly') == 1) {
            $(this).raty('readOnly', true);
        }
    });
});
