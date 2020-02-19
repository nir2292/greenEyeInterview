var slider = document.getElementById("myRange");
var button = document.getElementById("load-data");
var clusters = parseInt(slider.value);
var numberOfNeighbors = 5
button.innerHTML = clusters

slider.oninput = function() {
  clusters = this.value;
  button.innerHTML = clusters
}


document.getElementById("load-data").addEventListener("click",function(){

    var xmlhttp = new XMLHttpRequest();
    var url = "/clusters/" + clusters + "/";
    xmlhttp.open("GET", url);

    resetTable()

    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState === 4) {
          var parent = document.getElementById('base');
          initiateClusterTable(parent, clusters)
          parseResults(this.responseText)
        }
    };
    xmlhttp.send();
});


resetTable = function() {
  var parent = document.getElementById('base');
  parent.innerHTML = ''
}


initiateClusterTable = function(parent, clusters) {
  for (i = 0; i < clusters; i++) {
    var clusterList = document.createElement('ul');
    parent.appendChild(document.createElement('div').appendChild(clusterList));
    appendCanvasListItem(clusterList, "c" + i)
    for (j = 0; j < numberOfNeighbors; j++) {
      appendCanvasListItem(clusterList, "" + i + "_" + j)
    }
  }
}

appendCanvasListItem = function(parent,id) {
  var canv = document.createElement('canvas');
  canv.id = id;
  canv.width  = 30;
  canv.height = 30;
  parent.appendChild(document.createElement('li').appendChild(canv))
}


parseResults = function(resultsString) {
  var clustersStrings = resultsString.split("/----/")
  
  for (i = 0; i < clusters; i++) {

    var clusterCenter = document.getElementById("c" + i);
    draw64StringToCanvas(clustersStrings[getCenterInd(i)] , clusterCenter)

    for (j = 0; j < numberOfNeighbors; j++) {
      var clusterSample = document.getElementById("" + i + "_" + j);
      draw64StringToCanvas(clustersStrings[getClusterElemInd(i,j)] , clusterSample)
      
    }
  }
}

draw64StringToCanvas = function(str64, canv) {
    var ctx = canv.getContext('2d');
    var image = new Image();
    image.canv = canv
    image.onload = function() {
      var canv = this.canv;
      var ctx = canv.getContext('2d');
      ctx.drawImage(this, 0, 0);
    };
    image.src = "data:image/jpeg;base64," + str64;
}


getCenterInd = function(c) {
  ind = (numberOfNeighbors + 1) * c;
  if (ind > (clusters * (numberOfNeighbors + 1) - 1)) {
    return 0
  }
  return ind
}

getClusterElemInd = function(c,n) {
  ind = (numberOfNeighbors + 1) * c + 1 + n;
  if (ind > (clusters * (numberOfNeighbors + 1) - 1)) {
    return 0
  }
  return ind
}

