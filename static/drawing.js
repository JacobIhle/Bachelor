function Drawing(name, points, tags, creator, grade){
    this.name = name;
    this.points = points;
    this.tags = tags;
    this.creator = creator;
    this.grade = grade;
}


function updateDrawings() {
    if (currentImageLoaded) {
        canvasOverlay.context2d().strokeStyle = "rgba(255,0,0,1)";
        canvasOverlay.context2d().fillStyle = "rgba(255,0,0,1)";
        canvasOverlay.context2d().lineWidth = 200 / viewer.viewport.getZoom(true);

        if (tempDrawingPoints.length > 0) {
            if (tempDrawingPoints.length === 1) {
                canvasOverlay.context2d().beginPath();
                canvasOverlay.context2d().arc(tempDrawingPoints[0].x, tempDrawingPoints[0].y,
                    350 / viewer.viewport.getZoom(true), 0, 2 * Math.PI);
                canvasOverlay.context2d().fill();
                canvasOverlay.context2d().closePath();
            } else {
                drawDrawings(tempDrawingPoints);
            }
        }
        drawings.forEach(function (element) {
            var points = element.points;
            drawDrawings(points);
        });
    }
}

function drawDrawings(points) {
    canvasOverlay.context2d().beginPath();
    for (var i = 0; i < points.length; i++) {
        if (i === 0) {
            canvasOverlay.context2d().moveTo(points[i].x, points[i].y);
        } else if (i === points.length - 1) {
            canvasOverlay.context2d().lineTo(points[i].x, points[i].y);
            canvasOverlay.context2d().stroke();
            canvasOverlay.context2d().closePath();
        } else {
            canvasOverlay.context2d().lineTo(points[i].x, points[i].y);
        }
    }
}

function cancelDrawing() {
    tempDrawingPoints = [];
    try {
        canvasOverlay._updateCanvas();
    }
    catch (e) {
        console.log(e.message);
    }
    if (drawingEnabled) {
        toggleDrawing();
    }
    $("#Drawing").html("New Drawing");
    $("#DrawingTools").hide();
    $("#Dragging").attr("title", "Enable Dragging");
    $("#Dragging").css("background-color", "");
}

function toggleDrawing() {
    (drawingEnabled) ? drawingEnabled = false : drawingEnabled = true;
}

