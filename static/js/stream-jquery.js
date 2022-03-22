$(document).ready(function () {

    $("#about-btn").click(function (event) {
        msgstr = $("#msg").html();
        msgstr = msgstr + "ooo";
        $("#msg").html(msgstr);
    });

    $("img").hover(function(){
        $(this).css("box-shadow : 10px 10px 10px 5px gray,10px 10px 10px 5px blueviolet");
    });
});