window.onload = function() {

    var fileloader = document.getElementById("file");
    fileloader.onchange = function() {
    var images = document.getElementsByClassName("hr");
    for (let i = 0; i < images.length; i++) {
        images[i].remove();
    }
        var s = "";
        if (this.files.length > 3) {
            alert('Превышен лимит по количеству файлов');

            document.getElementById('file').value = "";
        }
        else {
        var objectURL = window.URL.createObjectURL(this.files[0]);
        //
        var files = this.files;
        if (!files.length) {
    fileList.innerHTML = "<p>No files selected!</p>";
  } else {
    var list = document.createElement("ul");
    list.setAttribute("class", "hr")
    for (var i = 0; i < files.length; i++) {
      var li = document.createElement("li");
      list.appendChild(li);

      var img = document.createElement("img");
      img.setAttribute("class", "preview");
      if ((window.screen.width > 1200) && (window.screen.height > 640)) {
        img.style.height = 75 + 'px';
        img.style.width = 105 + 'px';

      }
      img.src = window.URL.createObjectURL(files[i]);

      img.onload = function() {
        window.URL.revokeObjectURL(this.src);
      }
      li.appendChild(img);

    }
  }
  document.getElementById("preview").appendChild(list);
        //
        var c = 0;
        for (var i = 0; i < this.files.length; i++) {

            if (this.files[i].name.length > 16) {

                s =  s + "  |  " + this.files[i].name.slice(0, 9) + '...' + this.files[i].name.slice(-7, -1) + this.files[i].name[this.files[i].name.length - 1];
            } else {s = s + "  |  " + this.files[i].name;}

            c = c + this.files[i].size;
            if (c > 100 * 1024 * 1024) {
                s = "";
                alert('Превышен лимит по размеру файлов');
                document.getElementById('file').value = "";

                break
            }
        }

    }

if (s != "") {
s =s + "  |  ";
}
document.getElementById("filelist").innerHTML = s;
}
    var cur_url = window.location.href;
   cur_url = cur_url.split('?')[0];
   var links = document.getElementsByClassName('menu');
   for (let i = 0; i < links.length; i++) {
        if (links[i] == cur_url) {
            links[i].style.color = '#F4A460';
            break;
        }

   }

}
