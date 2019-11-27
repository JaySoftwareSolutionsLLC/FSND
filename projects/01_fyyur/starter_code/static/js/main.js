$('button.delete-venue').on('click', function() {
    let thisVenueId = $(this).attr('data-id');
    let confirmation = confirm(`Are you sure you want to delete venue ${thisVenueId}?`);
    if (confirmation) {
        $.ajax({
            url: `/venues/${thisVenueId}`,
            method: 'DELETE',
        })
        .always(function() {
            window.location.replace('/venues');
        });
    }
})