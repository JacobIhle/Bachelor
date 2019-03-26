var viewer;
var imageUrl;
var overlay;
var i = 0;
var aborts = 0;
var canvasObjects = [];
var drawings = [];
var drawingEnabled = false;

//TODO
/*
frontend buttons(JACOB): new drawing, finish drawing, toggle dragging/drawing stuff, undo button
migrate drawings to their own objectstructure thingie
import drawings
export drawings
give finished drawing name and tags and description
 */

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
        showNavigationControl: false,

        navigatorId: "",
        showNavigator: true,
    });
}


function addNonViewerHandlers() {
    $("#H281").on("click", function () {
        imageUrl = "scnImages/H281.scn";
        addViewerHandlers();
        open_slide(imageUrl);
    });

    $(".imageLinks").on("click", function () {
        var id = this.id;
        var name = id.replace(new RegExp("{space}", "g"), " ");
        imageUrl = "https://histology.ux.uis.no/app/" + name;


        open_slide(imageUrl);
        addViewerHandlers();
        $("#filename").text(name.split("/")[1]);
    })
}

function open_slide(url) {

    drawings = [];

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


    overlay = viewer.canvasOverlay({
        onRedraw:function(){
            //TODO REFACTOR
            //this + draw saved drawing objects
            console.log("redraw");
            overlay.context2d().strokeStyle = "rgba(255,0,0,1)";
            overlay.context2d().lineWidth = 200/viewer.viewport.getZoom(true);

            if(canvasObjects.length > 0) {
                if(canvasObjects.length === 1){
                    overlay.context2d().beginPath();
                    overlay.context2d().arc(canvasObjects[0].x, canvasObjects[0].y,
                        200/viewer.viewport.getZoom(true), 0, 2*Math.PI);
                    overlay.context2d().stroke();
                    overlay.context2d().closePath();
                }else {
                    overlay.context2d().beginPath();
                    for (var i = 0; i < canvasObjects.length; i++) {
                        if (i === 0) {
                            overlay.context2d().moveTo(canvasObjects[i].x, canvasObjects[i].y);
                        } else if (i === canvasObjects.length - 1) {
                            overlay.context2d().lineTo(canvasObjects[i].x, canvasObjects[i].y);
                            overlay.context2d().stroke();
                            overlay.context2d().closePath();
                        } else {
                            overlay.context2d().lineTo(canvasObjects[i].x, canvasObjects[i].y);
                        }
                    }
                }
            }

            drawings.forEach(function (element) {
                var points = element.points;
                overlay.context2d().beginPath();
                for(var i=0; i<points.length; i++){
                    if(i === 0){
                        overlay.context2d().moveTo(points[i].x, points[i].y);
                    }else if(i === points.length-1){
                        overlay.context2d().lineTo(points[i].x, points[i].y);
                        overlay.context2d().stroke();
                        overlay.context2d().closePath();
                    }else{
                        overlay.context2d().lineTo(points[i].x, points[i].y);
                    }
                }
            });

        },
        clearBeforeRedraw:true
    });


    $(window).resize(function() {
        overlay.resize();
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

    viewer.addHandler("canvas-click", function (e) {
        var pos = viewer.viewport.viewerElementToImageCoordinates(e.position);
        var posview = viewer.viewport.imageToWindowCoordinates(pos);
        var posviewport = viewer.viewport.imageToViewportCoordinates(pos);
        console.log(e.position);
        console.log(pos);
        console.log(posview);
        console.log(posviewport);
    });

    viewer.addHandler("open-failed", function () {
        fetch("https://histology.ux.uis.no/authenticated")
            .then(function (response) {
                if (response.status === 401) {
                    window.location.reload(true);
                    if(aborts === 0){
                        alert("You have been logged out for inactivity");
                        aborts++;
                    }

                }
            });
    });

    viewer.addHandler("tile-load-failed", function () {
        fetch("https://histology.ux.uis.no/authenticated")
            .then(function (response) {
                if (response.status === 401) {
                    window.location.reload(true);
                    if(aborts === 0){
                        alert("You have been logged out for inactivity");
                        aborts++;
                    }
                }
            });
    });

    viewer.addHandler('canvas-click', function(e) {
        if(drawingEnabled) {
            e.preventDefaultAction = true;
            var pos = viewer.viewport.viewerElementToImageCoordinates(e.position);

            canvasObjects.push({x: pos.x, y: pos.y});

            if (canvasObjects.length > 0) {
                overlay._updateCanvas();
            }
        }else{
            e.preventDefaultAction = false;
        }
    });

    viewer.addHandler('canvas-drag', function (e) {
        if(drawingEnabled){
            e.preventDefaultAction = true;
        }else{
            e.preventDefaultAction = false;
        }
    })

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

    $("#imageList").click(function () {
        $("#imageExplorer").toggle();
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

        $(this).siblings(".imageLinks").toggle();
    });


    $("#Drawing").click(function () {
        if ($(this).text() === "New Drawing"){
            toggleDrawing();
            $("#Drawing").html("Save Drawing");
            console.log("new");


        }else if($(this).text() === "Save Drawing"){
            //TODO
            //prompt user for name and tags
            if(canvasObjects.length > 1) {
                //add to database
                //save data to xml file
                drawings.push(new Drawing("name", canvasObjects, ["tag1", "tag2"]));
            }
            canvasObjects = [];
            toggleDrawing();
            $("#Drawing").html("New Drawing");
            console.log("save");
        }
    });

    $("#Dragging").click(function () {
        if ($("#Dragging").attr("title") === "Enable Dragging") {
            $("#Dragging").attr("title", "Disable Dragging");
            $("#Dragging").css("background-color", "#757575");
        } else if ($("#Dragging").attr("Title") === "Disable Dragging") {
            $("#Dragging").attr("title", "Enable Dragging");
            $("#Dragging").css("background-color", "");
        }
        toggleDrawing();
    });

    $("#UndoButton").click(function () {
        if(canvasObjects.length > 0) {
            canvasObjects.pop();
        }
        overlay._updateCanvas();
    });

    $("#CancelDrawing").click(function () {
        if(confirm("Confirm Cancellation")){
            canvasObjects = [];
            overlay._updateCanvas();
            toggleDrawing();
            $("#Drawing").html("New Drawing");

        }
    });

    $("#DownloadXML").click(function () {
        var xml = generateXML();
        download("file.xml", xml);
    });
}

function toggleDrawing() {
    if(drawingEnabled){
        drawingEnabled = false;
    }else{
        drawingEnabled = true;
    }
}

function generateXML() {
    var xml = document.implementation.createDocument("", "", null);

    var annotations = xml.createElement("Annotations");
    var annotation = xml.createElement("Annotation");
    var regions = xml.createElement("Regions");

    drawings.forEach(function (drawing) {
        var points = drawing.points;
        var region = xml.createElement("Region");
        var vertices = xml.createElement("Vertices");
        
        points.forEach(function (point) {
            var vertex = xml.createElement("Vertex");
            vertex.setAttribute("X", ""+point.x);
            vertex.setAttribute("Y", ""+point.y);
            vertex.setAttribute("Z", "0");
            vertices.appendChild(vertex);
        });

        region.appendChild(vertices);
        regions.appendChild(region);
    });

    annotation.appendChild(regions);
    annotations.appendChild(annotation);
    xml.appendChild(annotations);
    
    var serializer = new XMLSerializer();

    return serializer.serializeToString(xml);
}

function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}
