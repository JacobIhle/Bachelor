function sendXMLtoServer(xml, action) {
    if (currentImageLoaded) {
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                if (action === 1) {
                    XMLtoDrawing(xml);
                }
            } else if (this.readyState == 4) {
                alert("Something went wrong, please try again.");
            }
        };
        xmlHttp.open("POST", "postxml/" + currentImageLoaded.substring(0, currentImageLoaded.length - 4));
        xmlHttp.send(jQuery.parseXML(xml));
    }
}

function getXMLfromServer() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            XMLtoDrawing(xmlHttp.responseXML);
            canvasOverlay._updateCanvas();
        }
    };
    xmlHttp.open("GET", "getxml/" + currentImageLoaded.substring(0, currentImageLoaded.length - 4) + ".xml");
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

function downloadXML(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
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