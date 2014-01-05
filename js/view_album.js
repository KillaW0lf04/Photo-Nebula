function update_current_photo(elem) {
//            var name = "<b>" + $(elem).find('.name').val() + "</b>";
//            var author = "<b>" + $(elem).find('.user').val() + "</b>";
//            var date = "<b>" + $(elem).find('.date').val() + "</b>"
//
//            $('#photo_name').html(name + ' by ' + author + ' on ' + date);
}

var $container = $('#container');

$container.imagesLoaded( function(){
  $container.isotope({
      // options
      itemSelector : '.item',
      layoutMode : 'fitRows'
    });
});

$container.isotope({
  getSortData : {
    name : function ( $elem ) {
      return $elem.find('.name').val();
    },
    date : function ( $elem ) {
      return Date.parse($elem.find('.date').val());
    },
    author: function ( $elem ) {
      return $elem.find('.user').val();
    }
  }
});

var date_ascending = true;
var name_ascending = true;
var author_ascending = true;

$('#shuffle').click(function() {
    $container.isotope('shuffle');
});

$('#dateSort').click(function() {
    date_ascending = !date_ascending;

    $container.isotope({
        sortBy: 'date',
        sortAscending: date_ascending
    });
});

$('#nameSort').click(function() {
    name_ascending = !name_ascending;

    $container.isotope({
        sortBy: 'name',
        sortAscending: name_ascending
    });
});

$('#authorSort').click(function() {
    author_ascending = !author_ascending;

    $container.isotope({
        sortBy: 'author',
        sortAscending: author_ascending
    })
});