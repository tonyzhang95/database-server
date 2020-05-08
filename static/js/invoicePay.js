$(function() {
    $('#btnInvoice').click(function() {
        $.ajax({
            url: '/showPay?' + $('#invoice_form').serialize(),
            data: $('#invoice_form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (result, status, xhr) {
                console.log(result);
                $("#result").html(result.response);
                },
            error: function (xhr, status, error) {
                $("#result").html("Error: " + xhr.responseText)
                }
        })
    });
});
