$(document).ready(function(){
  // As global variable, defining the blinking function
  var DisplayingSearch = setInterval(function(){
    $("#message").fadeOut(500).fadeIn(500);
  }, 1000);
  //var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  //var socket = io.connect('http://www.example.com');
  var socket = io.connect(location.protocol + "//" + document.domain + ':' + location.port);
  
  socket.on('connect', function() {
    socket.send("hi")
  });

  socket.on("message", function(msg){
    console.log(msg);
  });

  socket.on("myresponse", function(json){
    $("#result").append("<a href=\"" + json.url + "\">" + json.head + "</a><br>");
    console.log(json);
  });

  socket.on("startcomplete", function(msg){
    if (msg == "DONE") {
      clearInterval(DisplayingSearch);
      //Re-defining the global variable without "var"
      $("#message").text("Completed");
      $("#message").fadeOut(1500);
      DisplayingSearch = "";
    } else if (msg == "Executing scraping") {
      $("#message").text("Searching!")
      //console.log(msg);
    }
  });

  $("#sendurlandword").on("click", function(){
    //socket.emit("my event", {"url": $("#url").val(), "word": $("#word").val()});
    var url = $("#url").val();
    var word = $("#word").val();
    var array = [url, word];
    try{
      socket.emit("myevent", array);
    } catch(e) {
      console.log(e);
    }
    console.log(array)
    $("#url").val("");
    $("#word").val("");
    $("#result").empty();
    if (DisplayingSearch == "") {
      DisplayingSearch = setInterval(function(){
        $("#message").fadeOut(500).fadeIn(500);
      }, 1000);
    }
  });
});