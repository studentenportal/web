$(function() {
    var lecturer_elem = $('h1.lecturer-name');
    var lecturer_pk = lecturer_elem.attr('data-lecturer-pk');
    var url = lecturer_elem.attr('data-rating-url');

    var submitScore = function(category, score) {
        var data = {'category': category, 'score': score};
        $.post(url, data, lecturerRatingCallback);
    };
    var lecturerRatingCallback = function(data) {
        var rating_count_text = data.rating_count == 1 ? ' Bewertung' : ' Bewertungen';
        var label = $('label[for="rating_' + data.category +'"]');
        label.attr('title', data.rating_count + rating_count_text);
        label.text(data.rating_avg + "/10");
    };
    $('[name="rating_d"]').change(function() {
        submitScore("d", $(this).val());
    });
    $('[name="rating_m"]').change(function() {
        submitScore("m", $(this).val());
    });
    $('[name="rating_f"]').change(function() {
        submitScore("f", $(this).val());
    });
});


$(function() {
    $('.drating').each(function(){
        var rating = $(this);
        var document_pk = rating.attr('data-document-pk');
        rating.find('[name="drating"]').change(function() {
            var score = $(this).val();
            var url = rating.attr('data-url');
            var summary_url = rating.attr('data-summary-url');
            $.ajax({
                type: 'POST',
                url: url,
                data: {'score': score},
                error: function(jqXHR, textStatus, errorThrown) {
                    // Couldn't complete ajax request.
                    // Reset raty and show error message.
                    alert(errorThrown + ': ' + jqXHR.responseText);
                },
                success: function(data, textStatus, jqXHR) {
                    // Update average rating
                    var summary_label = rating.find('label[for="drating"]');
                    summary_label.load(summary_url)
                    // Update self rating
                    var match = url.match(new RegExp("/dokumente/"+ "(.*)" + "/" + "(.*)" + "/rate/"));
                    if(match.length == 3){
                        var document_pk = match[2]
                        var self_rating_label = $('td[for="self_rating_' + document_pk +'"]');
                        self_rating_label.text("Deine Bewertung (" +score + "/10)");
                    }
                }
            });
        });
    });
});
