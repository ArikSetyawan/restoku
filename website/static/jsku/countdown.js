function startTimer(duration, display) {
  var timer = duration, minutes, seconds;
  setInterval(function () {
      minutes = parseInt(timer / 60, 10)
      seconds = parseInt(timer % 60, 10);

      minutes = minutes < 10 ? "0" + minutes : minutes;
      seconds = seconds < 10 ? "0" + seconds : seconds;

      display.textContent = minutes + " " + ":" + " " + seconds;

      if (--timer < 0) {
          timer = duration;
      }
      if (parseInt(minutes) <= 0 && parseInt(seconds) <= 0) {
        $.removeCookie('exp')
        $.removeCookie('table')
        window.location.replace('http://127.0.0.1:5002/')
      }
  }, 1000);
}

window.onload = function () {
  if ($.cookie("table")) {
    exp = $.cookie("exp")
    now = Date.now()/1000
    exp = parseInt(exp)-now
    timer = Math.floor(exp)
    console.log($.cookie("exp") + "-" + now + "=" + timer)
    // if(parseInt(min*60)+sec != 0){
    //   var fiveMinutes = (parseInt(min*60)+sec);
    // }else{
    //   var fiveMinutes = 60 * 5;
    // }
    // console.log("waktu : "+ fiveMinutes)
    // var fiveMinutes = 60 * 5;
    fiveMinutes=timer
    display = document.querySelector('#time');
    startTimer(fiveMinutes, display);
  }
};