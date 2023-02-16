

window.onload = function() {
    document.body.style.opacity = 0.85;
}
if (window.innerWidth < 1300) {
        var lis = document.getElementsByClassName('menu_li');
        for (let i = 0; i < lis.length; i++) {
            lis[i].style.flexBasis = "100%";
        }
    }
    else {

    var lis = document.getElementsByClassName('menu_li');
        for (let i = 0; i < lis.length; i++) {
            lis[i].style.flexBasis = 100 / lis.length+"%";
        }


    }

window.addEventListener('resize', function(event) {

    if (window.innerWidth < 1300) {
        var lis = document.getElementsByClassName('menu_li');
        for (let i = 0; i < lis.length; i++) {
            lis[i].style.flexBasis = "100%";
        }
    }
    else {

    var lis = document.getElementsByClassName('menu_li');
        for (let i = 0; i < lis.length; i++) {
            lis[i].style.flexBasis = 100 / lis.length+"%";
        }


    }

}, true);


   var cur_url = window.location.href;
   cur_url = cur_url.split('?')[0];



   var links = document.getElementsByClassName('menu');
   for (let i = 0; i < links.length; i++) {

        if (links[i] == cur_url) {
            links[i].style.color = '#F4A460';
            break;
        }

   }
var xDown = null;
var yDown = null;


document.addEventListener('touchstart', handleTouchStart, false);
document.addEventListener('touchmove', handleTouchMove, false);

function handleTouchStart(evt) {
    xDown = evt.touches[0].clientX;
    yDown = evt.touches[0].clientY;
};



var c = 0;
function handleTouchMove(evt) {
    if ( ! xDown || ! yDown ) {
        return;
    }
    var links = [];
    var link1 = document.getElementsByClassName('menu');
    for (let i = 1; i < link1.length; i++) {
        links.push(link1[i]);
    }

    var xUp = evt.touches[0].clientX;
    var yUp = evt.touches[0].clientY;

    var xDiff = xDown - xUp;
    var yDiff = yDown - yUp;
    var used = false;
   if ( Math.abs( xDiff ) > 350 ) {/*most significant*/
        if ( xDiff > 0 ) {
            var used = false;
            for (let i = 0; i < links.length; i++) {
                if (cur_url == links[i]) {
                    used = true;
                    if (i == 0) {
                        document.body.style.opacity = 0.2;
                        window.location.replace(links[links.length - 1]);

                        }
                    else {
                         document.body.style.opacity = 0.2;
                        window.location.replace(links[i - 1]);
                        }

                }
            }
            if (used == false) {
                window.history.go(-1);
            }
        } else {
            var used = false;
            for (let i = 0; i < links.length; i++) {
                if (cur_url == links[i]) {
                    used = true;
                    if (i == (links.length - 1)) {
                         document.body.style.opacity = 0.2;
                         window.location.replace(links[0]);



                    }
                    else {
                        document.body.style.opacity = 0.2;
                        window.location.replace(links[i + 1]);
                    }

                }
            }

        }
    }

   if (used == true) {
        xDown = null;
        yDown = null;
        return;
   }

    if (Math.abs( yDiff ) > 150){ // Это вам, в общем-то, не надо, вы ведь только влево-вправо собираетесь двигать

        if (( yDiff < 0 ) && (window.pageYOffset == 0)) {
            if (c > 0){
            xDown = null;
            yDown = null;
            c = 0;
            document.body.style.opacity = 0.2;


            window.location.reload();

            return;
            }
            else {
                c = 1;
                xDown = null;
                yDown = null;
                return;
            }

        }
    }


    return;




};

setInterval (function(){
    c = 0;

}, 3000)
