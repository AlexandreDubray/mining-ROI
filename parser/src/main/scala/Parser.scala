package parser

import scala.io.Source
import java.io.File
import scala.collection.mutable.ListBuffer

sealed trait Parser {

  def sourceDir: String

  var minLat: Option[Double] = None
  var maxLat: Option[Double] = None
  var minLong: Option[Double] = None
  var maxLong: Option[Double] = None

  def parse(filepath: String) : Unit

  def getListOfFile() : List[File] = {
    val root = new File(sourceDir)
    if (root.exists && root.isDirectory) {
      root.listFiles.filter(_.isFile).toList
    } else {
      println("Error with the source directory")
      sys.exit(1)
    }
  }
  
  def updateLat(lat: Double) = {
    minLat match {
      case None => minLat = Some(lat)
      case Some(v) => {
        if (v > lat) {
          minLat = Some(lat)
        }
      }
    }
    maxLat match {
      case None => maxLat = Some(lat)
      case Some(v) => {
        if (v < lat) {
          maxLat = Some(lat)
        }
      }
    }
  }

  def updateLong(long: Double) = {
    minLong match {
      case None => minLong = Some(long)
      case Some(v) => {
        if (v > long) {
          minLong = Some(long)
        }
      }
    }
    maxLong match {
      case None => maxLong = Some(long)
      case Some(v) => {
        if (v < long) {
          maxLong = Some(long)
        }
      }
    }
  }

  def minLatitude() : Double = {
    minLat match {
      case None => {
        println("No minimum latitude has been found. Has the file been parsed?")
        sys.exit(1)
      }
      case Some(v) => v
    }
  }

  def maxLatitude() : Double = {
    maxLat match {
      case None => {
        println("No maximum latitude has been found. Has the file been parsed?")
        sys.exit(1)
      }
      case Some(v) => v
    }
  }

  def minLongitude() : Double = {
    minLong match {
      case None => {
        println("No minimum longitude has been found. Has the file been parsed?")
        sys.exit(1)
      }
      case Some(v) => v
    }
  }

  def maxLongitude() : Double = {
    maxLong match {
      case None => {
        println("No maximum longitude has been found. Has the file been parsed?")
        sys.exit(1)
      }
      case Some(v) => v
    }
  }

}

class MicrosoftParser(val source: String) extends Parser{

  override def sourceDir:String = source

  override def parse(filepath: String) : Unit = {
    import java.io.PrintWriter
    new PrintWriter(filepath) {
      getListOfFile().foreach((f: File) => {
        val l:List[(String, Double, Double)] = Source.fromFile(f).getLines.map((x: String) => {
          val s = x.split(",").slice(1,4)
          val long = s(1).toDouble
          val lat = s(2).toDouble
          updateLong(long)
          updateLat(lat)
          (s(0), long, lat)
        }).toList
      
        for (end <- 0 until l.length) {
          write(s"${l(end)._1} ${l(end)._2} ${l(end)._3}")
          if (end != l.length - 1) {
            if (l(end)._1 == l(end+1)._1) {
              write("\n\n")
            } else {
              write("\n")
            }
          }
        }
        write("\n")
      })
      close()
    }
  }
}

object MicrosoftParser {
  def apply() = new MicrosoftParser("./data/taxis-Beijing-Microsoft")
}

class KaggleParser(val source: String) extends Parser {

  override def sourceDir : String = source

  def isClose(x: (Double, Double), y: (Double, Double)) : Boolean = {
      val deltaThreshold = 1
      Math.abs(x._1 - y._1) < deltaThreshold && Math.abs(x._2 - y._2) < deltaThreshold
  }

  override def parse(filepath: String) : Unit = {
    import java.io.PrintWriter
    new PrintWriter(filepath) {
      for (line <- Source.fromFile(source).getLines.map((s: String) => s.split("\\["))) {
        val meta = line(0)
        if (meta.split(",")(7) == "\"False\"" && line.length > 3) {
          val pos = line.slice(2,line.length).map( (tup: String) => {
            val v = tup.split(",")
            while (! v(1).takeRight(1).charAt(0).isDigit) {
              v(1) = v(1).dropRight(1)
            }
            (v(0).toDouble, v(1).toDouble)
          })
          var prevPos = (-1.0,-1.0)
          if (isClose(pos(0), pos(1))) {
            prevPos = pos(0)
          } else if (pos.length >= 3) {
            if (isClose(pos(1), pos(2))) {
              prevPos = pos(1)
            } else if (isClose(pos(0), pos(2))) {
              prevPos = pos(0)
            }
          }
          write(pos.filter( (x:(Double, Double)) => {
            val toReturn = isClose(prevPos, x)
            if(toReturn)
              prevPos = x
            toReturn
          }).mkString(" "))
          write("\n")
        }
      }
      close()
    }
  }
}

object KaggleParser {
  def apply() = new KaggleParser("./data/taxis-Kaggle.csv")
}
