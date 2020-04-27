$(function() {
    $('#btnCarInsSubmit').click(function() {
        $.ajax({
            url: '/processCarIns?' + $('#car_ins_form').serialize(),
            data: $('#car_ins_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#result").html(result.response);
                // if (result.response == "success") window.location.href='/userHome'
                },
            error: function (xhr, status, error) {
                $("#result").html(xhr.responseText)
                }
        })
    });
});
