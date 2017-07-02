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
            $("#talk").html(json.success_message);
        } else {
        $("#talk").empty()
        $("#talk").html(json.type[0]);
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


function fetch_schedule() {
    console.log("create post is working!") // sanity check
    var formData = $("#selectionform").serializeArray()
    jQuery('#container').empty();
    console.log(formData)
        $.ajax({
            url: "/ajax_schedule", // the endpoint
            type: "POST", // http method
            data: formData, // data sent with the post request

            // handle a successful response
            success: function (json) {
                console.log("success - next is json"); // another sanity check
                console.log(json.calendar); // log the returned json to the console

                for(desknum=0; desknum<json.desks.length; desknum++ ) {
                    console.log(json.cal_rows[desknum])
                    var table = $('<table class="table table-bordered table-striped"><caption>' + json.desks[desknum] + '</caption></table>').addClass('cal');
                    var row = $('<th></th>').addClass('cal').text(json.desks[desknum]);
                    table.append(row);
                    for (i = 0; i < json.calendar.length; i++) {
                        var row = $('<th style="padding: 5px;"></th>').addClass('cal').text(json.calendar[i]);
                        table.append(row);
                    };

                    for (i = 0; i < json.cal_rows[desknum].length; i++) {
                        var row = $('<tr><td></td></tr>').addClass('cal').text(json.cal_rows[desknum][i][0]);//name is added

                        for (d = 0; d < json.calendar.length; d++) {
                            row.append('<td>' + json.cal_rows[desknum][i][d + 1] + '</td>');
                            table.append(row);

                        };


                    };


                    $('#container').append(table);} ;           },





            error:function(json){
                console.log("somethings wrong")
            },
});
};

function controller_pto_report() {
    console.log("create post is working!") // sanity check
    var formData = $("#pto_report").serializeArray()
    jQuery('#container').empty();
        $.ajax({
            url: "/ajax_user_pto_report", // the endpoint
            type: "POST", // http method
            data: formData, // data sent with the post request

            // handle a successful response
            success: function (json) {
                console.log(json); // another sanity check

                var table = $('<table class="table table-bordered table-striped"><caption>PTO Report</caption></table>');
                var row = $('<th>Date</th><th>Date Requested</th><th>Assigned Coverage</th><th>Type</th><th>Approved</th><th>Cancel</th>');
                table.append(row);
                console.log(json["report"][0]["date_pto_taken"])
                for(ptoevent=0; ptoevent<json['report'].length; ptoevent++ ) {
                    var row = $('<tr><td>'+json['report'][ptoevent]["date_pto_taken"]+'</td><td>'+json["report"][ptoevent]["date_requested"]+'</td><td>'
                        +json["report"][ptoevent]["coverage_id"]+'</td>' +
                        '<td>'+json["report"][ptoevent]["type"]+'</td>' +
                        '<td>'+json["report"][ptoevent]["supervisor_approval"]+'</td>' +
                        '<td>Cancel</td></tr>');
                    table.append(row);}
                    ;

                $('#container').append(table);
                },





            error:function(json){
                console.log("somethings wrong")
            },
});
};

