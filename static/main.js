/*
Copyright (C) 2009 CodePlex Foundation
Copyright (C) 2010-2013 OpenSeadragon contributors

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

- Neither the name of CodePlex Foundation nor the names of its contributors
  may be used to endorse or promote products derived from this software
  without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*/
var serverUrl = "https://histology.ux.uis.no";
var viewer;
var aborts = 0;
var allTags = [];
var drawings = [];
var canvasOverlay;
var currentImageUrl;
var currentImageLoaded;
var tempDrawingPoints = [];
var drawingEnabled = false;
var searchTagEnabled = false;
var finishingDrawing = false;

$(document).ready(function () {
    updateAllTags(0);
    initializeCanvas();
    addNonViewerHandlers();
    addGuiHandlers();
    addXmlHandlers();
    addDrawingHandlers()
});

function initializeCanvas() {

    if (viewer) {
        viewer.close();
        $("#display").text("");
    }

    viewer = OpenSeadragon({
        id: "display",
        zoomPerScroll: 1.10,
        animationTime: 0.5,
        tileSource: currentImageUrl,
        showNavigationControl: false,

        navigatorId: "",
        showNavigator: true,
    });

    addOverlays();
    addViewerHandlers();
}

function addOverlays() {
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


    canvasOverlay = viewer.canvasOverlay({
        onRedraw: function () {updateDrawings();},
        clearBeforeRedraw: true
    });

}

function addNonViewerHandlers() {

    $(".imageLinks").on("click", function () {
        if (tempDrawingPoints.length === 0) {
            changeImage(this);
        } else if (confirm("Changing image will cancel drawing, continue?")) {
            changeImage(this);
        }
    })
}

function changeImage(image) {
    if (currentImageLoaded) {
        cancelDrawing();
    }
    var id = image.id;
    currentImageLoaded = id.replace(new RegExp("{space}", "g"), " ");
    currentImageUrl = serverUrl + "/app/" + currentImageLoaded;

    open_slide(currentImageUrl);
    getXMLfromServer();
}

function open_slide(url) {
    drawings = [];
    viewer.open(url);

    $(window).resize(function () {
        canvasOverlay.resize();
    });
}
