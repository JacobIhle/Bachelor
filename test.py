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
                ]
            }
        }
    }
}

print(foo["Histology"]["mary"]["poppins"])
foo["Histology"]["mary"]["poppinses"] = "hei"
print(foo["Histology"]["mary"]["poppinses"])

def recursiveFuck(dict):

    for key, value in dict.items():
        if type(value) is list:
            print("<div class=" + key + ">")
            for image in value:
                print("<div id="+image+"></div>")
            print("</div>")
            return
        else:
            print("<div class="+key+">")
            recursiveFuck(value)
            print("</div>")
    return


#recursiveFuck(foo)
