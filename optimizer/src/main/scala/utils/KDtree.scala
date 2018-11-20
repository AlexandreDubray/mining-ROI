package utils

import scala.io.Source

object Axis extends Enumeration {
  type Axis = Value
  val LATITUDE, LONGITUDE = Value
}

class KDTree(filepath: String, minimumSupport: Int) {
  import Axis._

  class KDTreeNode(val lowLat: Double, val highLat: Double, lowLong: Double, highLong: Double, axis: Axis) {


    val children = getChildren()

    def getChildren() : Option[(KDTreeNode, KDTreeNode)] = {
      if (axis == LATITUDE) {
        splitLatitude()
      } else {
        splitLongitude()
      }
    }

    def splitLatitude() : Option[(KDTreeNode, KDTreeNode)] = {
      val midLat = lowLat + (highLat - lowLat)/2.0
      if (g.shouldSplitOnLat(lowLat, highLat, lowLong, highLong)) {
        Some((new KDTreeNode(lowLat, midLat, lowLong, highLong, LONGITUDE), new KDTreeNode(midLat, highLat, lowLong, highLong, LONGITUDE)))
      } else {
        None
      }
    }

    def splitLongitude() : Option[(KDTreeNode, KDTreeNode)] = {
      val midLong = lowLong + (highLong - lowLong)/2.0
      if (g.shouldSplitOnLong(lowLat, highLat, lowLong, highLong)) {
        Some((new KDTreeNode(lowLat, highLat, lowLong, midLong, LATITUDE), new KDTreeNode(lowLat, highLat, midLong, highLong, LATITUDE)))
      } else {
        None
      }
    }

    def getDivisions() : List[(Double, Double, Double, Double)] = {
      children match {
        case None => List((lowLat, highLat, lowLong, highLong))
        case Some((left, right)) => List(left.getDivisions(), right.getDivisions()).flatten
      }
    }
  }

  val (minLat, maxLat, minLong, maxLong) = (41.100542, 41.249139, -8.7222031, -8.529393)
  val g = new Graph(20, 20, minLat, maxLat, minLong, maxLong)
  g.processFile(filepath)

  val root = new KDTreeNode(minLat, maxLat, minLong, maxLong, LATITUDE)

  def write_tree(destination_file: String) : Unit = {
    import java.io.PrintWriter
    new PrintWriter(destination_file) {
      val divisions = root.getDivisions()
      divisions.foreach( (x:(Double,Double,Double,Double)) =>
        write(s"${x._1} ${x._2} ${x._3} ${x._4}\n")
      )
      close()
    }
  }
}

object KDTree {
  def apply(filepath: String) = new KDTree(filepath, 2000)
}
