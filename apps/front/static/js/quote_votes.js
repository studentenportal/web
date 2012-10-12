$(document).ready(function() {
    $('.votebuttons div').click(function() {
        if ($(this).hasClass('active')) {
            var vote = 'remove';
        } else {
            var vote = $(this).hasClass('upvote') ? 'up' : 'down';
        }
        var quote_pk = $(this).parent().attr('data-quote-pk');
        Dajaxice.apps.front.vote_quote(quote_vote_callback, {'vote': vote, 'quote_pk': quote_pk});
    });
});

function quote_vote_callback(data) {
    wrapper = $('.votebuttons[data-quote-pk=' + data.quote_pk + ']');
    if (data.vote == 'up') {
        wrapper.children('.downvote').removeClass('active');
        wrapper.children('.upvote').addClass('active');
    } else if (data.vote == 'down') {
        wrapper.children('.upvote').removeClass('active');
        wrapper.children('.downvote').addClass('active');
    } else {
        wrapper.children('.upvote').removeClass('active');
        wrapper.children('.downvote').removeClass('active');
    }
    wrapper.children('.vote_sum').text(data.vote_sum);
    wrapper.attr('title', data.vote_count + ' Votes');
}
