/**
 * Created by Todd Hagler on 6/3/2017.
 */

$(function() {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});



function select_month(obj) {
    obj.style.backgroundColor = "#224acc";
}


// AJAX for posting
function create_post() {
    console.log("create post is working!") // sanity check
    var formData = $("#pto_form").serializeArray()
    console.log(formData)
        $.ajax({

        url : "/pto", // the endpoint
        type : "POST", // http method
        data : formData, // data sent with the post request

        // handle a successful response
        success : function(json) {
        console.log("success - next is json"); // another sanity check
        console.log(json.type); // log the returned json to the console
        if(json.pto_added >0) {
            $('#id_date_pto_taken').val('');
            $('#id_notes').val('');
            $("#talk").empty()
            $("#talk").prepend("<li><strong>"+json.success_message+"</span></li>");;
        } else {
        $("#talk").prepend("<li><strong>"+json.type[0]+"</span></li>");
        console.log("success"); // another sanity check
}},


        // handle a non-successful response
        error : function(json) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });

};
