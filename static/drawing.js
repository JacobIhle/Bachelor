function Drawing(name, points, tags, creator, grade){
    this.name = name;
    this.points = points;
    this.tags = tags;
    this.creator = creator;
    this.grade = grade;
}


function updateDrawings() {
    if (currentImage) {
        overlay.context2d().strokeStyle = "rgba(255,0,0,1)";
        overlay.context2d().fillStyle = "rgba(255,0,0,1)";
        overlay.context2d().lineWidth = 200 / viewer.viewport.getZoom(true);

        if (canvasObjects.length > 0) {
            if (canvasObjects.length === 1) {
                overlay.context2d().beginPath();
                overlay.context2d().arc(canvasObjects[0].x, canvasObjects[0].y,
                    350 / viewer.viewport.getZoom(true), 0, 2 * Math.PI);
                overlay.context2d().fill();
                overlay.context2d().closePath();
            } else {
                drawDrawings(canvasObjects);
            }
        }
        drawings.forEach(function (element) {
            var points = element.points;
            drawDrawings(points);
        });
    }
}

function drawDrawings(points) {
    overlay.context2d().beginPath();
            for (var i = 0; i < points.length; i++) {
                if (i === 0) {
                    overlay.context2d().moveTo(points[i].x, points[i].y);
                } else if (i === points.length - 1) {
                    overlay.context2d().lineTo(points[i].x, points[i].y);
                    overlay.context2d().stroke();
                    overlay.context2d().closePath();
                } else {
                    overlay.context2d().lineTo(points[i].x, points[i].y);
                }
            }
}

function cancelDrawing() {
    canvasObjects = [];
    try {
        overlay._updateCanvas();
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

function addDrawingHandlers() {
    $("#Drawing").click(function () {
        if (!finishingDrawing && currentImage) {
            if ($(this).text() === "New Drawing") {
                $("#DrawingTools").show();
                toggleDrawing();
                $("#Drawing").html("Save Drawing");


            } else if ($(this).text() === "Save Drawing") {
                $("#tagSelector").css("display", "");
                finishingDrawing = true;
                $(this).removeClass("drawingHover");

                updateAllTags(1);

                $("#DrawingTools").hide();
                if (canvasObjects.length > 1) {
                    canvasObjects.push(canvasObjects[0]); //snap to start
                    overlay._updateCanvas();
                }
                toggleDrawing();
            }
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
        if (canvasObjects.length > 0) {
            canvasObjects.pop();
        }
        overlay._updateCanvas();
    });

    $("#CancelDrawing").click(function () {
        if (confirm("Confirm Cancellation")) {
            cancelDrawing();
        }
    });
}