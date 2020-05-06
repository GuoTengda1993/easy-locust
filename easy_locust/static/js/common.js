function post_api(url) {
    var data = {
        "weight": $('#weight').val(),
        "url": $('#url').val(),
        "method": $('#method').val(),
        "query": $('#query').val(),
        "request_data": $('#request-data').val(),
        "expect_status_code": $('#expect-code').val(),
        "expect_str": $('#expect-str').val()
    };
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
            response = JSON.parse(data);
            if (response.msg === 'success') {
                window.location.reload();
            } else {
                alert(response.msg)
            }
        },
        error: function () {
            alert('Error happened.. Life was like a box of chocolates, you never know what you’re gonna get.')
        }
    });
}

function post_slave(url) {
    var data = {
        "ip": $('#ip').val(),
        "username": $('#username').val(),
        "password": $('#password').val()
    };
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
            response = JSON.parse(data);
            if (response.msg === 'success') {
                window.location.reload();
            } else {
                alert(response.msg)
            }
        },
        error: function () {
            alert('Error happened.. Life was like a box of chocolates, you never know what you’re gonna get.')
        }
    });
}

function post_config(url) {
    var data = {
        "host": $('#host').val(),
        "min_wait": $('#min-wait').val(),
        "max_wait": $('#max-wait').val(),
        "request_mode": $('#request-mode').val(),
        "token": $('#token').val(),
        "run_in_order": $('#run-in-order').val(),
        "content_type": $('#content-type').val()
    };
    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function (data) {
            response = JSON.parse(data);
            if (response.msg === 'success') {
                window.location.reload();
            } else {
                alert(response.msg)
            }
        },
        error: function () {
            alert('Error happened.. Life was like a box of chocolates, you never know what you’re gonna get.')
        }
    });
}