foo = {
    "Histology": {
            "mary": {
                "poppins": {
                    "peter": {
                        "parker": ["H281.scn"]

                    }
                },
                "jane": {
                    "Watson": ["H382_03A.scn"]

                }
            }
        },
    "Already anonymous": {
        "some": {
            "other": {
                "images": [
                    "H2352.scn",
                    "H9989.scn"
                ],
                "images1": [
                    "H2352.scn",
                    "H9989.scn"
                ],
                "images2": [
                    "H2352.scn",
                    "H9989.scn"
                ],
                "images3": [
                    "H2352.scn",
                    "H9989.scn"
                ]
            }
        }
    }
}



def RecursiveFuck(dict, returnString):

    for key, value in dict.items():
        if type(value) is list:
            returnString = returnString+"<div class=" + key + ">\n"
            for image in value:
                returnString = returnString +"<div id="+image+"></div>\n"
                returnString = returnString +"</div>\n"
        else:
            returnString = returnString +"<div class="+key+">\n"
            RecursiveFuck(value)
            returnString = returnString +"</div>\n"
    return


def CallFromJinja(dict):

    returnString = ""
    RecursiveFuck(dict, returnString)
    return returnString

#RecursiveFuck(foo)
