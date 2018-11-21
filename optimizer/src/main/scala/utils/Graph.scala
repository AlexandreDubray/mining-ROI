package utils

import scala.io.Source

class Graph(val width: Int,val height: Int, val minLat: Double, val maxLat: Double, val minLong: Double, val maxLong: Double) {
  val n = width*height
  val deltaLat = maxLat - minLat
  val deltaLong = maxLong - minLong
  val ratioLat = deltaLat / height
  val ratioLong = deltaLong / width
  
  val closenessThreshold = 0.0001

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

  def ternaryLat(lowLat: Double, highLat: Double, lowLong: Double, highLong: Double) : Double = {
    val minCol = getCol(lowLong)
    val maxCol = getCol(highLong)
    val minRow = getRow(lowLat)
    val maxRow = getRow(highLat)

    val l1 = lowLat + (highLat - lowLat)/3.0
    val l2 = lowLat + (2.0*(highLat - lowLat))/3.0
    if (getRow(l1) == getRow(l2) || Math.abs(l1-l2) < closenessThreshold) {
      l1
    } else {
      val f1 = fluxInsideRegion(minCol, maxCol, minRow, getRow(l1))
      val f2 = fluxInsideRegion(minCol, maxCol, minRow, getRow(l2))
      if (f1 < f2) {
        ternaryLat(l1, highLat, lowLong, highLong)
      } else if (f1 > f2) {
        ternaryLat(lowLat, l2, lowLong, highLong)
      } else {
        ternaryLat(l1, l2, lowLong, highLong)
      }
    }
  }

  def splitOnLat(lowLat: Double, highLat: Double, lowLong: Double, highLong: Double) : Option[Double] = {
    val minRow = getRow(lowLat)
    val maxRow = getRow(highLat)
    val minCol = getCol(lowLong)
    val maxCol = getCol(highLong)
    if (getRow(lowLat) == getRow(highLat) || Math.abs(lowLat - highLat) < closenessThreshold || fluxInsideRegion(minCol, maxCol, minRow, maxRow) < minimumSupport) {
      None
    } else {
      Some(ternaryLat(lowLat, highLat, lowLong, highLong))
    }
  }

  def ternaryLong(lowLat: Double, highLat: Double, lowLong: Double, highLong: Double) : Double = {
    val minCol = getCol(lowLong)
    val maxCol = getCol(highLong)
    val minRow = getRow(lowLat)
    val maxRow = getRow(highLat)

    val l1 = lowLong + (highLong - lowLong)/3.0
    val l2 = lowLong + (2.0*(highLong - lowLong))/3.0
    if (getCol(l1) == getCol(l2) || Math.abs(l1 - l2) < closenessThreshold) {
      l1
    } else {
      val f1 = fluxInsideRegion(minCol, getCol(l1), minRow, maxRow)
      val f2 = fluxInsideRegion(minCol, getCol(l2), minRow, maxRow)
      if (f1 < f2) {
        ternaryLong(minLat, highLat, l1, highLong)
      } else if (f1 > f2) {
        ternaryLong(minLat, highLat, lowLong, l2)
      } else {
        ternaryLong(minLat, highLat, l1, l2)
      }
    }
  }

  def splitOnLong(lowLat: Double, highLat: Double, lowLong: Double, highLong: Double) : Option[Double] = {
    val minRow = getRow(lowLat)
    val maxRow = getRow(highLat)
    val minCol = getCol(lowLong)
    val maxCol = getCol(highLong)
    if (getCol(lowLong) == getCol(highLong) || Math.abs(lowLong - highLong) < closenessThreshold || fluxInsideRegion(minCol, maxCol, minRow, maxRow) < minimumSupport) {
      None
    } else {
      Some(ternaryLong(lowLat, highLat, lowLong, highLong))
    }
  }
}
