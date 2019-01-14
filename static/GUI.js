var viewer;
var imageID;
var dziInfo;

$(document).ready(function() {
    addNonViewerHandlers();
});

function addNonViewerHandlers() {
    $("#testButton").on("click", function () {
        imageID = "dziFolder/H281-03/H281.dzi";
        fetch(imageID)
            .then(response => response.text())
            .then(text => dziInfo);

        open_slide(imageID);
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

    viewer = new Seadragon.Viewer("display");

    viewer.config.animationTime = 0.5;
    viewer.config.blendTime = 0.1;
    viewer.config.zoomPerScroll = 1.05;

    viewer.clearControls();
    viewer.openDzi(url, dziInfo);
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

    viewer.add_animationfinish(function () {
        $("#currentZoomLevel").html(Math.round(viewer.viewport.getZoom(true) * 100) / 100 + "x");
    });

    viewer.add_open(function () {
        viewer.viewport.zoomTo(0.6);
    });

}


