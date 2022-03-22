$(document).ready(function () {

    $("#about-btn").click(function (event) {
        msgstr = $("#msg").html();
        msgstr = msgstr + "ooo";
        $("#msg").html(msgstr);
    });

    $(".icon").hover(function(){
        $(this).css("box-shadow" , "1px 1px 1px 1px #3d3d3d,4px 4px 4px 2px darkslateblue");
        }, function(){
        $(this).css("box-shadow" , "0px 0px 0px 0px white,0px 0px 0px 0px white");
      });
});