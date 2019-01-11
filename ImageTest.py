
from flask import Flask, send_file, make_response, render_template


app = Flask(__name__)




@app.route('/')
def main():
    return render_template("testOpenseadragon.html")

@app.route('/<folder>/<level>/<tile>')
def getTile(folder, level, tile):
    return send_file(folder+"/"+level+"/"+tile)

if __name__ == '__main__':
    app.run(port=5000)






