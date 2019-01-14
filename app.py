from flask import Flask, send_file, make_response, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return render_template("testOpenseadragon.html")

@app.route('/<root>/<imageID>/<dzFiles>/<level>/<tile>')
def getTile(root ,imageID ,dzFiles, level, tile):
    return send_file(root+"/"+imageID+"/"+dzFiles+"/"+level+"/"+tile)

@app.route('/<root>/<imageID>/<file>')
def getDzi(root, imageID, file):
    return send_file(root+"/"+imageID+"/"+file)

if __name__ == '__main__':
    app.run(port=5000)






