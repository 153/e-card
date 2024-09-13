  var socket = io();
  var uname = $.cookie("uname");
  var uid = $.cookie("uid");  
  console.log($.cookie());
  console.log($.cookie("uname"));

  socket.emit('join lobby', uname, uid);

  socket.on('join lobby', function(player){
      if (player == uname)
	  return;
      $('#players').append($(`<li id="${player}">${player} </li>`));
      $('#' + player).append($(` <button class="challenge" value="${player}">Challenge</button>`));
  });

  socket.on('leave lobby', function(player){
      $('#' + player).remove();
  });
  
  socket.on('lobby message', function(msg){
      $('#messages').append($('<li>').text(msg));
  });

  socket.on('lobby challenge', function(msg){
      console.log(msg);
      var from = msg.from;
      var to = msg.to;
      console.log(from, to);
      if (to == uname) {
	  $('#' + from).children("button:first").remove();
	  $('#' + from).append(` <button class="challenge" value="${from}">Accept</button>`);
      };  
  });
		    
  $(document).ready(function () {
      $('#n').val(uname);
  });

  $('body').on('click', '.challenge', function() {
      var clicked = $(this).val();
      console.log(clicked);
      socket.emit("lobby challenge", {"from":uname, "to":clicked});
  });
  
  $('form').submit(function(){
      socket.emit('lobby message', uname + ": " + $('#m').val());
      console.log($('#m').val());
      $('#m').val('');
      return false;
  });
