function update_current_photo(elem) {
    var name = "<b>" + $(elem).find('.name').val() + "</b>";
    var author = "<b>" + $(elem).find('.user').val() + "</b>";
    var date = "<b>" + $(elem).find('.date').val() + "</b>"

    $('#selected_photo').html(name + ' by ' + author);
}

function validate_form() {
    var value = $('#photo_file').val();
    var name = $('#photo_name').val();

    if(value == "")
    {
        alert("Please select a Photo to upload");
        return false;
    }

    if(name == "")
    {
        alert("Please specify a name for the Photo being uploaded");
        return false;
    }

    return true;
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