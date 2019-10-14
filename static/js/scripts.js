function ajax(method, url, data) {
    data = typeof data !== 'undefined' ? data : [];
    var result = null;
    var request = $.ajax({
        type: method,
        url: url,
        data: data,
        async: false,
        complete: function () {
        }, //manage the complete if needed
        success: function (response) {
            /*if (response.result !== 1) {
                let message = response.message;

                if (typeof response.message !== 'string') {
                    result = response.message;
                    message = 'Перевірте правильність введенних даних';
                }
                new PNotify({
                    text: message,
                    type: 'error',
                    styling: 'bootstrap3',
                    delay: 3000
                });
            } else {
                new PNotify({
                    text: response.message,
                    type: 'success',
                    styling: 'bootstrap3',
                    delay: 3000
                });
            }*/
        },
        error: function (response) {
            /*new PNotify({
                text: response.message,
                type: 'error',
                styling: 'bootstrap3',
                delay: 3000
            });*/
        }
    });
    request.done(function(response) {
        result = response;
    });
    return result;
}