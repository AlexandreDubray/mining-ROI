package utils

import scala.io.Source

object Axis extends Enumeration {
  type Axis = Value
  val LATITUDE, LONGITUDE = Value
}

class KDTree(filepath: String, minimumSupport: Int) {
  import Axis._

  def buffer = Source.fromFile(filepath)

  class KDTreeNode(val lowLat: Double, val highLat: Double, lowLong: Double, highLong: Double, axis: Axis) {

    println(s"Node that englobe $lowLat to $highLat (latitude) and $lowLong to $highLong (longitude)")

    val children = getChildren()

    def getChildren() : Option[(KDTreeNode, KDTreeNode)] = {
      if (axis == LATITUDE) {
        splitLatitude()
      } else {
        splitLongitude()
      }
    }

    def splitLatitude() : Option[(KDTreeNode, KDTreeNode)] = {
      println("Splitting on latitude")
      val midLat = lowLat + (highLat - lowLat)/2.0
      val leftSupport = countTrajectories(lowLat, midLat, lowLong, highLong)
      val rightSupport = countTrajectories(midLat, highLat, lowLong, highLong)
      println(s"Left support is $leftSupport, right support is $rightSupport (minSup $minimumSupport)")
      if (leftSupport >= minimumSupport && rightSupport >= minimumSupport) {
        Some((new KDTreeNode(lowLat, midLat, lowLong, highLong, LONGITUDE), new KDTreeNode(midLat, highLat, lowLong, highLong, LONGITUDE)))
      } else {
        None
      }
    }

    def splitLongitude() : Option[(KDTreeNode, KDTreeNode)] = {
      println("Splitting on longitude")
      val midLong = lowLong + (highLong - lowLong)/2.0
      val upperSupport = countTrajectories(lowLat, highLat, lowLong, midLong)
      val bottomSupport = countTrajectories(lowLat, highLat, midLong, highLong)
      println(s"Upper support is $upperSupport, bottom support is $bottomSupport (minSup $minimumSupport)")
      if (upperSupport >= minimumSupport && bottomSupport >= minimumSupport) {
        Some((new KDTreeNode(lowLat, highLat, lowLong, midLong, LATITUDE), new KDTreeNode(lowLat, highLat, midLong, highLong, LATITUDE)))
      } else {
        None
      }
    }
  }

  val (minLat, maxLat, minLong, maxLong) = (41.100542, 41.249139, -8.7222031, -8.529393)
  val root = new KDTreeNode(minLat, maxLat, minLong, maxLong, LATITUDE)

  def find_bounds() : (Double, Double, Double, Double)= {
    var min_lat: Option[Double] = None
    var max_lat: Option[Double] = None
    var min_long: Option[Double] = None
    var max_long: Option[Double] = None
    buffer.getLines().filter(!_.isEmpty()).foreach( (x:String) => {
      x.split(" ").foreach( (y: String) => {
        val v = y.substring(1).dropRight(1).split(",")
        val long = v(0).toDouble
        val lat = v(1).toDouble
        min_lat match {
          case None => min_lat = Some(lat)
          case Some(v) => if (v > lat) min_lat = Some(lat)
        }
        max_lat match {
          case None => max_lat = Some(lat)
          case Some(v) => if (v < lat) max_lat = Some(lat)
        }
        min_long match {
          case None => min_long = Some(long)
          case Some(v) => if (v > long) min_long = Some(long)
        }
        max_long match {
          case None => max_long = Some(long)
          case Some(v) => if (v < long) max_long = Some(long)
        }
      })
    })
    (min_lat.get, max_lat.get, min_long.get, max_long.get)
  }

  def countTrajectories(lowLat: Double, highLat: Double, lowLong: Double, highLong: Double) : Int = {
    import scala.util.control._
    var loop = new Breaks
    var counter = 0
      buffer.getLines().foreach( (x:String) => {
        loop.breakable {
          x.split(" ").foreach( (y: String) => {
            val v = y.substring(1).dropRight(1).split(",")
            val long = v(0).toDouble
            val lat = v(1).toDouble
            if (lowLat <= lat && lat <= highLat && lowLong <= long && long <= highLong) {
              counter += 1
              loop.break
            }
          })
        }
      })
    counter
  }

}

object KDTree {
  def apply(filepath: String) = new KDTree(filepath, 2000)
}
