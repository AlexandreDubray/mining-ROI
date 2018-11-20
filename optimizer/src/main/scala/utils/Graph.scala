package utils

import scala.io.Source

class Graph(val width: Int,val height: Int, val minLat: Double, val maxLat: Double, val minLong: Double, val maxLong: Double) {
  val n = width*height
  val deltaLat = maxLat - minLat
  val deltaLong = maxLong - minLong
  val ratioLat = deltaLat / height
  val ratioLong = deltaLong / width
  
  val flux = Array.fill[Int](n,n)(0)
  val inFlux = Array.fill[Int](n)(0)
  var nTrajectories = 0

  def minimumSupport: Int = 0.05*nTrajectories toInt

  def mapPosToNode(lat: Double, long: Double) : Int = {
    val col = if (long == maxLong) width-1 else ((long-minLong)/ratioLong).toInt
    val row = if (lat == maxLat) height-1 else ((lat-minLat)/ratioLat).toInt
    row*width + col
  }

  def getLongLat(representation: String) : (Double, Double) = {
    val l = representation.substring(1).dropRight(1).split(",")
    (l(0).toDouble, l(1).toDouble)
  }

  def getRow(latitude: Double) : Int = {
    if (latitude == maxLat) {
      height - 1
    } else {
      ((latitude - minLat)/ratioLat).toInt
    }
  }

  def getCol(longitude: Double) : Int = {
    if (longitude == maxLong) {
      width -1
    } else {
      ((longitude - minLong)/ratioLong).toInt
    }
  }

  def link(n1: Int, n2: Int) : Unit = {
    flux(n1)(n2) += 1
    inFlux(n2) += 1
  }

  def processFile(filepath: String) : Unit = {
    val buffer = Source.fromFile(filepath)
    for (trajectory <- buffer.getLines()) {
      nTrajectories = nTrajectories + 1
      val positions = trajectory.split(" ")
      for (i <- 0 until positions.length - 1) {
        val (long1, lat1) = getLongLat(positions(i))
        val (long2, lat2) = getLongLat(positions(i+1))
        val node1 = mapPosToNode(lat1, long1)
        val node2 = mapPosToNode(lat2, long2)
        link(node1, node2)
      }
    }
  }

  def fluxInsideRegion(minCol: Int, maxCol: Int, minRow: Int, maxRow: Int) : Int = {
    val nodes: Array[Int] = Array.tabulate[Array[Int]](maxRow - minRow + 1) { (row: Int) =>
      Array.tabulate[Int](maxCol - minCol + 1) { (col: Int) =>
        (minRow + row)*width + (minCol + col)
      }
    }.flatten
    var f = 0
    for (i <- 0 until nodes.length) {
      f = f + inFlux(nodes(i))
      for (j <- i+1 until nodes.length) {
        f = f - flux(nodes(i))(nodes(j))
        f = f - flux(nodes(j))(nodes(i))
      }
    }
    f
  }

  def shouldSplitOnLat(lowLat: Double, highLat: Double, lowLong: Double, highLong: Double) : Boolean = {
    val midLat = lowLat + (highLat - lowLat)/2.0
    val minRow = getRow(lowLat)
    val midRow = getRow(midLat)
    val maxRow = getRow(highLat)
    val minCol = getCol(lowLong)
    val maxCol = getCol(highLong)
    fluxInsideRegion(minCol, maxCol, minRow, midRow) >= minimumSupport && fluxInsideRegion(minCol, maxCol, midRow + 1, maxRow) >= minimumSupport
  }

  def shouldSplitOnLong(lowLat: Double, highLat: Double, lowLong: Double, highLong: Double) : Boolean = {
    val midLong = lowLong + (highLong - lowLong)/2.0
    val minRow = getRow(lowLat)
    val maxRow = getRow(highLat)
    val minCol = getCol(lowLong)
    val midCol = getCol(midLong)
    val maxCol = getCol(highLong)
    fluxInsideRegion(minCol, midCol, minRow, maxRow) >= minimumSupport && fluxInsideRegion(midCol+1, maxCol, minRow, maxRow) >= minimumSupport
  }
}
