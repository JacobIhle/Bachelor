var viewer;
var imageUrl;
var dziInfo;

$(document).ready(function() {
    addNonViewerHandlers();
    jacobisGUIstuff();
});

function addNonViewerHandlers() {
    $("#testButton").on("click", function () {
        imageUrl = "scnImages/H281";
        //fetch(imageUrl)
        //    .then(response => response.text())
        //    .then(text => dziInfo);

        open_slide(imageUrl);
        addViewerHandlers();
    })
}

function open_slide(url) {
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
    viewer.open(url);
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
    })

    /*viewer.add_animationfinish(function () {
        $("#currentZoomLevel").html(Math.round(viewer.viewport.getZoom(true) * 100) / 100 + "x");
    });

    viewer.add_open(function () {
        viewer.viewport.zoomTo(0.6);
    });
    */
}

function jacobisGUIstuff(){
    $("#menuicon").hover(function(){
        $("#menuicon").css({"background-color": "#212121", "border-radius": "5px"});
    }, function(){
        $("#menuicon").css({"background-color": "#424242", "border-radius": "5px"});
    });

    $("a").hover(function(){
        $("#menuicon").css({"background-color": "#212121", "border-radius": "5px"});
    }, function(){
        $("#menuicon").css({"background-color": "#424242", "border-radius": "5px"});
    });
}



