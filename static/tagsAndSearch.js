function fetchSearchTags(searchValue) {
    fetch("https://histology.ux.uis.no/searchTagEnabled", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({"tag": searchValue})
    })
        .then(res => res.json())
        .then(data => filterImagesByTag(data["images"]));
}

function filterImagesByTag(dbResult) {
    var imageLinks = $(".imageLinks").toArray();

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

function filterImages(value, searchValue) {
    value.forEach(function (element) {
        if (!element.innerHTML.includes(searchValue)) {
            $(element).hide();
        }
        if (element.innerHTML.includes(searchValue)) {
            $(element).show();
        }
    });
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

function tagSaveSubmit(creator) {
    var name = $("#tagName").val();
    var grade = $("#tagGrade").val();

    var tags = [];
    $("#tagsForm select").each(function () {
        tags.push($(this).val())
    });

    if (tempDrawingPoints.length > 1) {
        tempDrawingPoints.push(tempDrawingPoints[0]);
        var drawing = new Drawing(name, tempDrawingPoints, tags, creator, grade);
        drawings.push(drawing);
        canvasOverlay._updateCanvas();
        sendXMLtoServer(generateXML([drawing]), 0)
    }
    tempDrawingPoints = [];
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

    addTagHandlers();
}

