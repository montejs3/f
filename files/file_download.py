import gdown
import zipfile

url = "https://drive.google.com/uc?id=1hUhwMC2iWWTP-Yil0wNrnpfMRZA33Ci2"
output = "files/files_server.zip"

gdown.download(url, output, quiet=False)

# Now we unzip the file
with zipfile.ZipFile(output, "r") as zip_file:
    # extract all
    zip_file.extractall("files")
    print("unziped all")


