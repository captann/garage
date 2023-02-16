window.onload = function () {
  var width = 0;
  var mas = document.getElementsByClassName('input')
  for (let i = 0; i < mas.length; i++) {
    if (mas[i].offsetWidth > width) {
        width = mas[i].offsetWidth;
    }
  }
  for (let i = 0; i < mas.length; i++) {
    mas[i].setAttribute("display", "inline-block");
    mas[i].setAttribute("width", '' + 100 + "px");
  }
}
