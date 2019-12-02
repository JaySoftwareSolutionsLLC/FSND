$('button.delete-venue').on('click', function() {
    let thisVenueId = $(this).attr('data-id');
    let confirmation = confirm(`Are you sure you want to delete venue ${thisVenueId}?`);
    if (confirmation) {
        $.ajax({
            url: `/venues/${thisVenueId}`,
            method: 'DELETE',
        })
        .always(function(response) {
            // alert(JSON.stringify(response));
            window.location.replace('/venues');
        });
    }
})
$('button.delete-artist').on('click', function() {
    let thisArtistId = $(this).attr('data-id');
    let confirmation = confirm(`Are you sure you want to delete artist ${thisArtistId}?`);
    if (confirmation) {
        $.ajax({
            url: `/artists/${thisArtistId}`,
            method: 'DELETE',
        })
        .always(function(response) {
            // alert(JSON.stringify(response));
            window.location.replace('/artists');
        });
    }
})