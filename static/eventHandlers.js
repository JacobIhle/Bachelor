function addDrawingHandlers() {
    $("#Drawing").click(function () {
        if (!finishingDrawing && currentImageLoaded) {
            if ($(this).text() === "New Drawing") {
                $("#DrawingTools").show();
                toggleDrawing();
                $("#Drawing").html("Save Drawing");

            } else if ($(this).text() === "Save Drawing") {
                if (tempDrawingPoints.length > 1) {
                    $("#tagSelector").css("display", "");
                    finishingDrawing = true;
                    $(this).removeClass("drawingHover");
                    $("#DrawingTools").hide();

                    updateAllTags(1);
                    tempDrawingPoints.push(tempDrawingPoints[0]); //snap to start
                    canvasOverlay._updateCanvas();
                    toggleDrawing();

                } else {
                    cancelDrawing();
                }

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
        if (tempDrawingPoints.length > 0) {
            tempDrawingPoints.pop();
        }
        canvasOverlay._updateCanvas();
    });

    $("#CancelDrawing").click(function () {
        if (confirm("Confirm Cancellation")) {
            cancelDrawing();
        }
    });
}

function addViewerHandlers() {
    viewer.addHandler("animation-finish", function () {
        $("#currentZoomLevel").html(Math.round(viewer.viewport.getZoom(true) * 100) / 100 + "x");
    });

    viewer.addHandler("open", function () {
        viewer.viewport.zoomTo(0.6);
    });

    viewer.addHandler("open-failed", function () {
       fetchAuthenticated();
    });

    viewer.addHandler("tile-load-failed", function () {
        fetchAuthenticated();
    });

    viewer.addHandler('canvas-click', function (e) {
        if (drawingEnabled) {
            e.preventDefaultAction = true;
            var pos = viewer.viewport.viewerElementToImageCoordinates(e.position);

            tempDrawingPoints.push({x: pos.x, y: pos.y});

            if (tempDrawingPoints.length > 0) {
                canvasOverlay._updateCanvas();
            }
        } else {
            e.preventDefaultAction = false;
        }
    });

    viewer.addHandler('canvas-drag', function (e) {
        if (drawingEnabled) {
            e.preventDefaultAction = true;
        } else {
            e.preventDefaultAction = false;
        }
    })
}

function fetchAuthenticated(){
    fetch(serverUrl + "/authenticated")
    .then(function (response) {
        if (response.status === 401) {
            window.location.reload(true);
            if (aborts === 0) {
                alert("You have been logged out for inactivity");
                aborts++;
            }

        }
    });
}

function addXmlHandlers() {
    $("#DownloadXML").click(function () {
        if (currentImageLoaded) {
            var xml = generateXML(drawings);
            downloadXML(currentImageLoaded.substring(0, currentImageLoaded.length - 4) + ".xml", xml);
        } else {
            alert("No image selected");
        }
    });

    $("#UploadXML").click(function () {
        $("#FileInput").trigger("click");
    });

    $("#FileInput").on("change", function (e) {
        var file = e.target.files[0];
        var reader = new FileReader();
        reader.readAsText(file, "UTF-8");

        reader.onload = readerEvent => {
            var content = readerEvent.target.result;

            sendXMLtoServer(content, 1)
        }
    });
}

function addGuiHandlers() {
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

    $(".imageLinks").on("click", function () {
        if (tempDrawingPoints.length === 0) {
            changeImage(this);
        } else if (confirm("Changing image will cancel drawing, continue?")) {
            changeImage(this);
        }
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

    $("#searchField").click(function () {
        $(".folder").show();
        $(".imageLinks").show();
        if (searchTagEnabled) {
            populateSearchDropDown();
        }
    });

    $("#searchField").on("keyup", function (e) {
        var value = $(".imageLinks").toArray();
        var searchValue = $(this).val();
        if (!searchTagEnabled) {
            filterImages(value, searchValue);
        } else if (e.key === "Enter") {
            fetchSearchTags(searchValue);
        }
    });

    $("#searchTags").on("click", function () {
        if (searchTagEnabled) {
            $("#searchField").val("");
            $(".dropdown-search-content").empty();

            $(this).removeClass("searchTagsClicked");
            $(this).attr("id", "searchTags");
            searchTagEnabled = false;
        } else {

            $(this).addClass("searchTagsClicked");
            $(this).attr("id", " ");
            searchTagEnabled = true;
        }
    });
}

function addTagHandlers() {
    $("#addSelector").click(function () {
        generateTagSelector()
    });

    $("#tagSaveSubmit").on("click", function () {
        let result;
        fetch(serverUrl + "/getCurrentUser")
            .then(data => data.text())
            .then(text => result = text)
            .then(() => tagSaveSubmit(result));
    });

    $("#tagSaveCancel").on("click", function () {
        $("#tagSelector").css("display", "none");
        $("#DrawingTools").show();
        finishingDrawing = false;
        $("#Drawing").addClass("drawingHover");
        toggleDrawing();
        removeTagSelector();
    });


    $("#addTagButton").on("click", function () {
        var newTag = $("#addTagForm input").val();

        if (newTag !== "") {
            var selects = $("div select");
            fetch(serverUrl + "/addTag", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({"tag": newTag})
            }).then(function (response) {
                if (response.status === 200) {
                    allTags.push(newTag);
                    selects.each(function () {
                        $(this).append("<option>" + newTag + "</option>");
                    });
                }
            });
            updateAllTags(0);
        }

    })
}
