from flask import request, send_from_directory
from app import db
import xml.etree.ElementTree as ET
import traceback
import os

xmlStoragePath = "//home/prosjekt/Histology/thomaso/"


def saveFromXml(foldername, filename):
    grade = 0
    tags = []
    try:
        file = foldername + "[slash]" + filename + ".xml"
        if not os.path.isfile(xmlStoragePath + file):
            createXmlFileIfNotExist(xmlStoragePath + file)

        InsertImageToDB(file.replace(".xml", ""))

        tree = ET.parse(xmlStoragePath + file)
        regions = tree.getroot()[0][0]


        xml = request.data.decode("utf-8")
        xmlThing = ET.fromstring(xml)
        xmlTree = ET.ElementTree(xmlThing)

        newRoot = xmlTree.getroot()

        for region in newRoot.iter("Region"):
            regions.append(region)
            try:
                formatedTags = region.attrib["tags"]
                tags = formatedTags.split("|")
                grade = region.attrib["grade"]
            except:
                pass
            finally:
                InsertDrawingsToDB(file.replace(".xml", ""), tags, grade)

        tree.write(xmlStoragePath + file)
    except:
        traceback.print_exc()
        return "", 500
    return "", 200


def LoadFromXml(foldername, filename):
    file = foldername + "[slash]" + filename
    foo = file.replace("%20", " ")
    if os.path.isfile(xmlStoragePath + foo):
        return send_from_directory(xmlStoragePath, foo)
    return "", 500


def createXmlFileIfNotExist(path):
    Annotations = ET.Element("Annotations")
    Annotation = ET.SubElement(Annotations, "Annotation")
    ET.SubElement(Annotation, "Regions")
    tree = ET.ElementTree(Annotations)
    tree.write(path)


def InsertImageToDB(imagePath):
    query = "select ImagePath from images where ImagePath = '{}';".format(imagePath)
    queryResult = db.engine.execute(query)
    result = [row[0] for row in queryResult]

    if not result:
        db.engine.execute("insert into images(ImagePath) values('{}');".format(imagePath))


def InsertDrawingsToDB(imagePath, tags, grade):
    for tag in tags:
        queryResult = db.engine.execute("select ImagePath from annotations where tag = '{}'"
                                        " and ImagePath = '{}'".format(tag, imagePath))
        result = [row[0] for row in queryResult]

        if not result:
            db.engine.execute("insert into annotations(ImagePath, Tag, Grade) values('{}', '{}', '{}');"
                              .format(imagePath, tag, grade))
        else:
            dbResult = db.engine.execute("select ImagePath, Tag, Grade from annotations where ImagePath = '{}'"
                                         "and Tag = '{}' and Grade = '{}';".format(imagePath, tag, grade))

            resultDb = [res[0] for res in dbResult]

            if not resultDb:
                db.engine.execute("insert into annotations(ImagePath, Tag, Grade) values('{}', '{}', '{}');"
                                  .format(imagePath, tag, grade))