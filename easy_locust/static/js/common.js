function post_api(url) {
    var data = {
        "weight": parseInt($('#weight').val()),
        "url": $('#url').val(),
        "method": $('#method').val(),
        "query": $('#query').val(),
        "request_data": $('#request-data').val(),
        "expect_status_code": parseInt($('#expect-code').val()),
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

function put_config(url) {
    var data = {
        "host": $('#host').val(),
        "min_wait": parseFloat($('#min-wait').val()),
        "max_wait": parseFloat($('#max-wait').val()),
        "request_mode": $('#request-mode').val(),
        "run_in_order": parseInt($('#run-in-order').val()),
        "content_type": $('#content-type').val()
    };
    $.ajax({
        type: 'put',
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

function put_api(url) {
    var data = editor.session.getValue();
    $.ajax({
        type: 'put',
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

function del_api(url) {
    $.ajax({
        type: 'delete',
        url: url,
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

function operate_api(url) {
    $.ajax({
        type: 'get',
        url: url,
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

function collapse_api(id) {
    var element = $(id);
    if (element.hasClass('collapse')) {
        element.removeClass('collapse');
        element.addClass('collapse.in')
    } else {
        element.removeClass('collapse.in');
        element.addClass('collapse')
    }
}
