var viewer;
var imageUrl;
var currentImage;
var overlay;
var aborts = 0;
var canvasObjects = [];
var drawings = [];
var allTags = [];
var drawingEnabled = false;
var finishingDrawing = false;
var searchTags = false;

/*
TODO
merge jacobs shit in.
python get/post xml, change these to support our new database tag search stuff.
add logging here and there, get/post xml maybe?
remove "show log" from html dropdown menu
shouldnt be necessary to do anything on existing javascript for tagsearch thingie, make more thorough check to confirm this.
create unit tests -forked off to next years bachelor group.

fix searchfield height and tag button thingie height.
footer is not perfect, FIX IT U MONGRELS.

maybe maybe if time show full list of available tags to user
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


    overlay = viewer.canvasOverlay({
        onRedraw: function () {
            //TODO REFACTOR
            //this + draw saved drawing objects
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
                });
            }
        },
        clearBeforeRedraw: true
    });

}

function addNonViewerHandlers() {

    $(".imageLinks").on("click", function () {
        if (canvasObjects.length === 0) {
            changeImage(this);
        } else if (confirm("Changing image will cancel drawing, continue?")) {
            changeImage(this);
        }
    })
}

function changeImage(image) {
    cancelDrawing();
    var id = image.id;
    currentImage = id.replace(new RegExp("{space}", "g"), " ");
    imageUrl = "https://histology.ux.uis.no/app/" + currentImage;

    open_slide(imageUrl);
    getXMLfromServer();
}

function open_slide(url) {
    drawings = [];
    viewer.open(url);

    $(window).resize(function () {
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

    viewer.addHandler("open-failed", function () {
        fetch("https://histology.ux.uis.no/authenticated")
            .then(function (response) {
                if (response.status === 401) {
                    window.location.reload(true);
                    if (aborts === 0) {
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
                    if (aborts === 0) {
                        alert("You have been logged out for inactivity");
                        aborts++;
                    }
                }
            });
    });

    viewer.addHandler('canvas-click', function (e) {
        if (drawingEnabled) {
            e.preventDefaultAction = true;
            var pos = viewer.viewport.viewerElementToImageCoordinates(e.position);

            canvasObjects.push({x: pos.x, y: pos.y});

            if (canvasObjects.length > 0) {
                overlay._updateCanvas();
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

    $("#DownloadXML").click(function () {
        if (currentImage) {
            var xml = generateXML(drawings);
            download(currentImage.substring(0, currentImage.length - 4) + ".xml", xml);
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

    $("#searchField").click(function () {
        $(".folder").show();
        $(".imageLinks").show();

        var searchDropdown = $(".dropdown-search-content");

        if($(".dropdown-search-content a").length === 0) {
            allTags.forEach(function (tag) {
                searchDropdown.append("<a class='classTags'>" + tag + "</a>");
            });
        }
        $(".dropdown-search-content a").on("click", function () {
            $("#searchField").val($(this).html());
            $(".dropdown-search-content").empty();
            fetchSearchTags();
        });
    });

    $("#searchField").on("keyup", function (e) {
        var value = $(".imageLinks").toArray();
        var searchValue = $(this).val();
        //TODO: Refactor
        if (!searchTags) {
            value.forEach(function (element) {
                if (!element.innerHTML.includes(searchValue)) {
                    $(element).hide();
                }
                if (element.innerHTML.includes(searchValue)) {
                    $(element).show();
                }
            });
        } else if (e.key === "Enter") {
            fetchSearchTags();
        }
    });

    $("#searchTags").on("click", function () {
        var className = $(this).attr("class");
        if (className === "") {
            $(this).addClass("searchTagsClicked");
            $(this).attr("id", " ");
            searchTags = true;
        } else {
            $(this).removeClass("searchTagsClicked");
            $(this).attr("id", "searchTags");
            searchTags = false;
        }
    });
}


function fetchSearchTags() {
    var searchValue = $("#searchField").val();
    fetch("https://histology.ux.uis.no/searchTags", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({"tag": searchValue})
    })
        .then(res => res.json())
        .then(data => imageFilter(data["images"]));
}

function imageFilter(dbResult) {
    var imageLinks = $(".imageLinks").toArray();
    console.log(dbResult);

    imageLinks.forEach(function (imageLinksElement) {
        var match = false;
        dbResult.forEach(function (dbElement) {
            var foo = dbElement.replace(new RegExp(" ", "g"), "{space}");
            var element = foo.replace("[slash]", "/");
            if(imageLinksElement.id === element + ".scn"){
                match = true;
            }
        });

        if(match){
            $(imageLinksElement).show();
        }else{
            $(imageLinksElement).hide();
        }
        match = false;
    })
}

function updateAllTags(modifier) {
    if (modifier === 1) {
        fetch("https://histology.ux.uis.no/updateTags")
            .then(res => res.json())
            .then(data => allTags = data["tags"])
            .then(() => generateTagSelectorWindow());
    } else {
        fetch("https://histology.ux.uis.no/updateTags")
            .then(res => res.json())
            .then(data => allTags = data["tags"])
    }
}


function generateTagSelectorWindow() {
    var formName = "<form> Name: <input type='text' id='tagName' name='tagName'><br>" +
        "Grade: <select id = 'tagGrade'>\n" +
        "<option>1</option>\n" +
        "<option>2</option>\n" +
        "<option>3</option>\n" +
        "<option>4</option>\n" +
        "<option>5</option>\n" +
        "<option>6</option>\n" +
        "</select></form><br>";
    var plus = "<img src=\"../static/images/plus.svg\" id=\"addSelector\"> <br>";
    var tagsForm = "<form id=\"tagsForm\" method=\"POST\" action=\"/Tags\"><div></div></form>";

    var saveTags = "<div id=\"saveTags\">\n" +
        "<input type=\"submit\" id=\"tagSaveSubmit\">\n" +
        "<input type=\"button\" id=\"tagSaveCancel\" value=\"Cancel\">\n" +
        "</div>";

    var addTag = "<div id=\"addTag\">\n" +
        "<form id=\"addTagForm\">\n" +
        "Create new tag: <br> <input type=\"text\" name=\"addTag\" maxlength=\"32\">\n" +
        "</form>\n" +
        "<div id=\"addTagButton\">Add Tag</div>\n" +
        "</div>";

    var tagSelector = $("#tagSelector");

    tagSelector.append(formName);
    tagSelector.append(plus);
    tagSelector.append(tagsForm);
    tagSelector.append(saveTags);
    tagSelector.append(addTag);
    generateTagSelector();

    $("#addSelector").click(function () {
        generateTagSelector()
    });

    $("#tagSaveSubmit").on("click", function () {
        let result;
        fetch("https://histology.ux.uis.no/getCurrentUser")
            .then(data => data.text())
            .then(text => result = text)
            .then(() => tagSaveSubmit(result));
    });

    $("#tagSaveCancel").on("click", function () {
        //hide the name, tag display thingie
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
            fetch("https://histology.ux.uis.no/addTag", {
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


function tagSaveSubmit(creator) {
    var name = $("#tagName").val();
    var grade = $("#tagGrade").val();

    var tags = [];
    $("#tagsForm select").each(function () {
        tags.push($(this).val())
    });

    if (canvasObjects.length > 1) {
        canvasObjects.push(canvasObjects[0]);
        var drawing = new Drawing(name, canvasObjects, tags, creator, grade);
        drawings.push(drawing);
        overlay._updateCanvas();
        sendXMLtoServer(generateXML([drawing]), 0)
    }
    canvasObjects = [];
    $("#Drawing").html("New Drawing");

    finishingDrawing = false;
    $("#Drawing").addClass("drawingHover");

    removeTagSelector();
}

function removeTagSelector() {
    $("#tagSelector").css("display", "none");
    $("#tagSelector").empty();
}

function generateTagSelector() {
    //fetch array of tags from database
    var selectorHtml = "<div><select name='option'>";

    selectorHtml += "<option></option>";
    allTags.forEach(function (tag) {
        selectorHtml += "<option>" + tag + "</option>";
    });
    selectorHtml += "</select><img src=\"../static/images/trash.png\" class='deleteButtons'></div>";
    var selectElements = $("#tagsForm select");
    if (selectElements.length < 7) {
        $("#tagsForm").append(selectorHtml);
    }

    $(".deleteButtons").click(function () {
        $(this).parent().remove();
    });
}

function cancelDrawing() {
    canvasObjects = [];
    try {
        overlay._updateCanvas();
    } catch (e) {
        console.log("oops");
    }
    if (drawingEnabled) {
        toggleDrawing();
    }
    $("#Drawing").html("New Drawing");
    $("#DrawingTools").hide();
    $("#Dragging").attr("title", "Enable Dragging");
    $("#Dragging").css("background-color", "");
}

function sendXMLtoServer(xml, action) {
    if (currentImage) {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                if (action === 1) {
                    XMLtoDrawing(xml)
                }
            } else if (this.readyState == 4) {
                alert("Something went wrong, please try again.")
            }
        };
        xmlHttp.open("POST", "postxml/" + currentImage.substring(0, currentImage.length - 4));
        xmlHttp.send(jQuery.parseXML(xml));
    }
}


function getXMLfromServer() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            XMLtoDrawing(xmlHttp.responseXML)
        }
    };
    xmlHttp.open("GET", "getxml/" + currentImage.substring(0, currentImage.length - 4) + ".xml");
    xmlHttp.send();
}


function XMLtoDrawing(xml) {
    var regions = $(xml).find("Region");
    regions.each(function (i, region) {
        var name = $(region).attr("name");
        var points = [];
        var tags = String($(region).attr("tags"));
        var creator = $(region).attr("creator");
        var grade = $(region).attr("grade");

        var vertices = $(region).find("Vertex");
        vertices.each(function (i, vertex) {
            var x = $(vertex).attr("X");
            var y = $(vertex).attr("Y");
            points.push({x: x, y: y});
        });
        drawings.push(new Drawing(name, points, tags.split("|"), creator, grade));
    })
}


function toggleDrawing() {
    (drawingEnabled) ? drawingEnabled = false : drawingEnabled = true;
}

function generateXML(listOfDrawings) {
    var xml = document.implementation.createDocument("", "", null);

    var annotations = xml.createElement("Annotations");
    var annotation = xml.createElement("Annotation");
    var regions = xml.createElement("Regions");
    regions.textContent = "\n";

    listOfDrawings.forEach(function (drawing) {
        var points = drawing.points;
        var tags = drawing.tags;
        var name = drawing.name;
        var creator = drawing.creator;
        var grade = drawing.grade;
        var tagsAsString = "";

        for (let i = 0; i < tags.length; i++) {
            if (i === 0) {
                tagsAsString += tags[i];
            } else {
                tagsAsString += "|" + tags[i];
            }
        }

        var region = xml.createElement("Region");
        region.setAttribute("tags", tagsAsString);
        region.setAttribute("name", name);
        region.setAttribute("creator", creator);
        region.setAttribute("grade", grade);
        region.textContent = "\n";
        var vertices = xml.createElement("Vertices");
        vertices.textContent = "\n";

        points.forEach(function (point) {
            var vertex = xml.createElement("Vertex");
            vertex.setAttribute("X", "" + point.x);
            vertex.setAttribute("Y", "" + point.y);
            vertex.setAttribute("Z", "0");
            vertex.textContent = "\n";
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
