$.fn.raty.defaults.path = '/static/img/raty/';
$.fn.raty.defaults.number = 10;
$(document).ready(function() {
    $('#lrating-d').raty({
        starHalf: 'star-half-red.png',
        starOff: 'star-off-red.png',
        starOn: 'star-on-red.png'
    });
    $('#lrating-m').raty({
        starHalf: 'star-half-green.png',
        starOff: 'star-off-green.png',
        starOn: 'star-on-green.png'
    });
    $('#lrating-f').raty({
        starHalf: 'star-half-blue.png',
        starOff: 'star-off-blue.png',
        starOn: 'star-on-blue.png'
    });
});
