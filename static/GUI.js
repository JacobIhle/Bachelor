var viewer;
var imageUrl;
var overlay;
var i = 0;

$(document).ready(function () {
    addNonViewerHandlers();
    jacobisGUIstuff();
    initiallizeCanvas();
});

function initiallizeCanvas() {

    if (viewer) {
        // Never reuse an existing viewer to avoid a timer leak
        // (OpenSeadragon issue #14)
        viewer.close();
        $("#display").text("");
    }

    viewer = OpenSeadragon({
        id: "display",
        zoomPerScroll: 1.10,
        animationTime: 0.5,
        tileSource: imageUrl,

        navigatorId: "",
        showNavigator: true,
    });

    overlay = viewer.fabricjsOverlay({scale: 1});
}


function addNonViewerHandlers() {
    $("#H281").on("click", function () {
        imageUrl = "scnImages/H281.scn";
        open_slide(imageUrl);
        addViewerHandlers();
    });

    $(".imageLinks").on("click", function () {
        var image = this.id;
        console.log(image);
        imageUrl = "http://152.94.1.69:5000/" + image;
        open_slide(imageUrl);
        addViewerHandlers();
        $("#filename").text(image);
    })
}

function open_slide(url) {

    viewer.open(url);

    viewer.scalebar({
        stayInsideImage: false,
        backgroundColor: "#616161",
        fontColor: "white",
        color: "#212121",

        xOffset: 45,
        yOffset: 15,
        maxWidth: 0.18,
        pixelsPerMeter: 4000000
    });
}

function addViewerHandlers() {

    $("#zoom4x").on("click", function () {
        viewer.viewport.zoomTo(4);
    });

    $("#zoom10x").on("click", function () {
        viewer.viewport.zoomTo(10);
    });

    $("#zoom20x").on("click", function () {
        viewer.viewport.zoomTo(20);
    });

    $("#zoom40x").on("click", function () {
        viewer.viewport.zoomTo(40);
    });


    viewer.addHandler("animation-finish", function () {
        $("#currentZoomLevel").html(Math.round(viewer.viewport.getZoom(true) * 100) / 100 + "x");
    });

    viewer.addHandler("open", function () {
        viewer.viewport.zoomTo(0.6);
    });

    viewer.addHandler("animation-start", function () {
        overlay._canvasdiv.style.opacity = "0";
    });

    viewer.addHandler("animation-finish", function () {
        overlay._canvasdiv.style.opacity = "1";
    });

    viewer.addHandler("canvas-click", function (e) {
        var pos = viewer.viewport.viewerElementToImageCoordinates(e.position);
        var posview = viewer.viewport.imageToWindowCoordinates(pos);
        var posviewport = viewer.viewport.imageToViewportCoordinates(pos);
        console.log(pos);
        console.log(posview);
        console.log(posviewport);
    });
    /*
        viewer.addHandler("canvas-click", function (e) {
            e.preventDefaultAction = true;
            var pos1 = viewer.viewport.viewerElementToImageCoordinates(e.position);
            var pos = viewer.viewport.imageToViewportCoordinates(pos1);
            var rect = new fabric.Rect({
              left: pos.x-0.5025,
              top: pos.y-0.5025,
              fill: 'blue',
              width: 0.005,
              height: 0.005
            });
            overlay.fabricCanvas().add(rect);
        });
    */

}

function jacobisGUIstuff() {
    $("#menuicon").hover(function () {
        $("#menuicon").css({"background-color": "#212121", "border-radius": "5px"});
    }, function () {
        $("#menuicon").css({"background-color": "#424242", "border-radius": "5px"});
    });

    $("a").hover(function () {
        $("#menuicon").css({"background-color": "#212121", "border-radius": "5px"});
    }, function () {
        $("#menuicon").css({"background-color": "#424242", "border-radius": "5px"});
    });

    $("#infoButton").click(function () {
        var infoField = document.getElementById("infoField");
        if (infoField.style.display == "block") {
            infoField.style.display = "none"
        } else {
            infoField.style.display = "block"
        }
    });

    $("#H281").click(function () {
        $("#filename").text("H281-03");
    });

    $(".imageList").click(function () {
        $("#imageExplorer").toggle();
    });

    $("#imageExplorer").click(function () {
       var test = $(event.target);
       console.log(test)
    });



    $(".folderButtons").click(function () {
        event.stopPropagation();
        $(this).siblings(".folder").slideToggle("fast");
        var buttonColor = $(this).css("background-color");
        if (buttonColor.toString() === "rgb(62, 142, 65)") {
            $(this).css("background-color", "#4caf50"); // Light green
        } else {
            $(this).css("background-color", "#3e8e41"); // Dark green
        }
        console.log(buttonColor);

        $(this).siblings(".imageLinks").toggle();
    });
}
