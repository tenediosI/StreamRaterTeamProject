function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let csrftoken = $("[name=csrfmiddlewaretoken]").val();
function done () {
            alert("Profile has been Updated. \nReload to see visible changes.");
        }

$(document).ready(function () {

    $("#update-profile").click(function (e) {

        e.preventDefault();

        if (validateEmail($('#email').val())) {

            $.ajax({
                type: "POST",
                dataType: 'json',
                headers: {
                    "X-CSRFToken": csrftoken
                },
                data: {
                    email: $('#email').val(),
                    bio: $('#bio').val(),
                    csrfmiddlewaretoken: csrftoken,
                },
                success: done(),

            });
        } else {
            alert("Email invalid")
        }

    });

    function validateEmail(email){

        return !!((email.includes("@") && email.includes(".")) || email.trim()=='');
    }

});