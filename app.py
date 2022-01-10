from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/file")
def testFile():
    file = open("data/test-file.txt", "r")
    fileContent = file.read()
    file.close()
    return fileContent

if __name__ == "__main__":
    app.run()