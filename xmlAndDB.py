from flask import request
from app import db
import xml.etree.ElementTree as ET
import traceback
import os


def saveFromXml(foldername, filename):
    grade = 0
    tags = []
    try:
        folder = "//home/prosjekt/Histology/thomaso/"
        file = foldername + "[slash]" + filename + ".xml"
        if not os.path.isfile(folder + file):
            createXmlFileIfNotExist(folder + file)

        InsertImageToDB(file.replace(".xml", ""))

        tree = ET.parse(folder + file)
        regions = tree.getroot()[0][0]

        xml = request.data.decode("utf-8")
        xmlThing = ET.fromstring(xml)
        xmlTree = ET.ElementTree(xmlThing)

        newRegions = xmlTree.getroot()[0][0]
        moreRegions = newRegions.findall("Region")

        for region in moreRegions:
            regions.append(region)
            try:
                formatedTags = region.attrib["tags"]
                tags = formatedTags.split("|")
                grade = region.attrib["grade"]
            except:
                traceback.print_exc()
            finally:
                InsertDrawingsToDB(file.replace(".xml", ""), tags, grade)

        tree.write(folder + file)
        print("we got here")
    except:
        traceback.print_exc()
        return "", 500
    return "", 200


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
                                         "and Tag = '{}' and Grade = {};".format(imagePath, tag, grade))

            resultDb = [res[0] for res in dbResult]

            if not resultDb:
                db.engine.execute("insert into annotations(ImagePath, Tag, Grade) values('{}', '{}', '{}');"
                                  .format(imagePath, tag, grade))