from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from mnistloader import load_mnist
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import skimage
import base64

class KmeansData:

    def __init__(self):
        print("loading database...")
        (x_train, t_train), (x_test, t_test) = load_mnist(flatten=True, normalize=False)
        self.x_train = x_train[:2000]
        self.numberOfNeighborsToDisplay = 5


    def calculateKmeans(self, clusters):
        print("calculating kmeans for ", clusters, " clusters")
        db = self.x_train
        X = np.array(db)
        kmeans = KMeans(n_clusters=clusters, random_state=42).fit(X)
        self.setClusters(kmeans)
        return kmeans

    def setClusters(self, kmeans):
        print("initiating clusters list...")
        db = self.x_train
        self.clusters = [[center, []] for center in kmeans.cluster_centers_]
        i = 0
        fullCount = 0
        while i < len(db) and fullCount < len(self.clusters):
            sample = db[i]
            sampleLable = kmeans.labels_[i]
            neighList = self.clusters[sampleLable][1]
            n = self.numberOfNeighborsToDisplay
            if len(neighList) < n:
                neighList.append(sample)
                if len(neighList) == n:
                    fullCount += 1
            i += 1


class Serv(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.separator = "/----/"

    def parseImagesToSend(self):
        separator = "/----/"
        clusterImagesString = ""
        for i in range(len(kmeansData.clusters)):
            centerToString = np.array(kmeansData.clusters[i][0])
            centerToString = centerToString.astype(np.uint8).reshape(28, 28)
            clusterImagesString += self.imgTo64byteString(centerToString) + separator

            for j in range(len(kmeansData.clusters[i][1])):
                clusterToString = np.array(kmeansData.clusters[i][1][j]).reshape(28, 28)
                clusterImagesString += self.imgTo64byteString(clusterToString) + separator
        return clusterImagesString

    def imgTo64byteString(self, img):
        with BytesIO() as output_bytes:
            PIL_image = Image.fromarray(skimage.img_as_ubyte(img))
            PIL_image.save(output_bytes, 'JPEG')
            bytes_data = output_bytes.getvalue()
        return str(base64.b64encode(bytes_data), 'utf-8')

    def do_GET(self):

        if self.path == '/':
            self.path = '/index.html'
            file_to_open = open(self.path[1:]).read()

        elif self.path == '/main.js':
            file_to_open = open(self.path[1:]).read()

        elif self.path == '/main.css':
            file_to_open = open(self.path[1:]).read()

        elif self.path.startswith('/clusters/'):
            numOfClusters = int(self.path.split('/')[2])
            kmeansData.calculateKmeans(numOfClusters)
            clusterImagesString = self.parseImagesToSend()
            file_to_open = clusterImagesString

        else:
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))



print("initializing kmeans dataset...")
kmeansData = KmeansData()
print("initializing server...")
httpd = HTTPServer(('localhost', 8080), Serv)
print("ready")

httpd.serve_forever()

