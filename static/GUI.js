var viewer;
var imageID;
var dziInfo;

$(document).ready(function() {
    addNonViewerHandlers();
    jacobisGUIstuff();
});

function addNonViewerHandlers() {
    $("#H281").on("click", function () {
        imageUrl = "scnImages/H281";
        fetch(imageUrl)
            .then(response => response.text())
            .then(text => dziInfo);

        open_slide(imageID);
        addViewerHandlers();
    });
    $("#H142").on("click", function () {
        imageID = "scnImages/H282";
        fetch(imageID)
            .then(response => response.text())
            .then(text => dziInfo);

        open_slide(imageID);
        addViewerHandlers();
    });

    $("#H83").on("click", function () {
        imageID = "scnImages/H83";
        fetch(imageID)
            .then(response => response.text())
            .then(text => dziInfo);

        open_slide(imageID);
        addViewerHandlers();
    });
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

    $("#infoButton").click(function(){
        var infoField = document.getElementById("infoField");
        if (infoField.style.display == "block"){
            infoField.style.display = "none"
        } else {
            infoField.style.display = "block"
        }
      });
    $("#H281").click(function(){
        $("#filename").text("H281-03");
    });
    $("#H142").click(function(){
        $("#filename").text("H142-04");
    });
    $("#H83").click(function(){
        $("#filename").text("H83-06");
    });
}



