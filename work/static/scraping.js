$(document).ready(function(){
  // As global variable, defining the blinking function
  var DisplayingSearch = setInterval(function(){
    $("#message").fadeOut(500).fadeIn(500);
  }, 1000);
  //var socket = io.connect('http://www.example.com');
  var socket = io.connect(location.protocol + "//" + document.domain + ':' + location.port);
  //var blankstar = "static/blankstar.jpg";
  var n = 1;

  socket.on('connect', function() {
    socket.send("hi")
  });

  socket.on("message", function(msg){
    console.log(msg);
  });

  var n = 1;
  socket.on("myresponse", function(json){
    // var result = document.getElementById("result");
    // var a = document.createElement("a");
    // a.id = n;
    // a.href = json.url;
    // var head = document.createTextNode(json.head);
    // a.appendChild(head);
    // var send = document.createElement("button");
    // send.classList.add("sendbutton");
    // send.setAttribute("data-target", n);
    // var img = document.createElement("img");
    // var path = "http://www.example.com/static/blankstar.jpg";
    // img.src = path;
    // send.appendChild(img);
    // var br = document.createElement("br");
    // var persend = send.insertAdjacentHTML("afterend", br);
    // a.insertAdjacentHTML("afterend", persend);
    // result.appendChild(a);
    
    //data属性：data-*　はxmlのように任意のマークアップを施せる
    //button要素の中にあるdata-targetはその名の通り、targetとなる対象を指定している
    //今回の場合はidがｎ(数字)のもの　つまり、aタグ
    $("#result").append("<a id=\"" + n + "\" data-url=\"" + json.url + "\" data-head=\"" + json.head + 
    "\" href=\"" + json.url + "\">" + json.head + 
    "</a><button class=\"sendbutton\" id=\"sendunsendstar\" data-target=\"#" + n + "\"><img id=\"img" + 
    n + "\" src=\"" + "http://www.example.com/static/blankstar.jpg\"></button><br>");
    console.log(json);
    n++;
  });

  //You gotta envoke event in a way below for buttons generated dynamically
  $(document).on("click", "#sendunsendstar", function(){
    //"This" here refers <button> having the sendunsendstar id
    //.data("target") refers the <a> having the targeted id
    //.data('url) or .data('head) is "a" tag's data-url or data-head's attribute
    //so in this case, they're gonna be json.url and json.head 
    let bk_url = $($(this).data('target')).data('url');
    let bk_head = $($(this).data('target')).data('head');
    let bk_dict = { url:bk_url, head:bk_head};
    socket.emit("bk_db", bk_dict);
    //alert("Bookmarked")
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
    var link = $("#url").val();
    var word = $("#word").val();
    var array = { url: link, head: word };
    try{
      socket.emit("myevent", array);
    } catch(e) {
      console.log(e);
    }
    console.log(array);
    $("#url").val("");
    $("#word").val("");
    $("#result").empty();
    if (DisplayingSearch == "") {
      DisplayingSearch = setInterval(function(){
        $("#message").fadeOut(500).fadeIn(500);
      }, 1000);
    }
    n = 1;
  });
});