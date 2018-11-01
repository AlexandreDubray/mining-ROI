package webapp

import util._

import org.singlespaced.d3js.d3
import org.singlespaced.d3js.Ops._

import scala.scalajs.js
import org.scalajs.dom
import org.scalajs.dom._
import org.scalajs.dom.ext.Ajax

import scala.util.Random
import scala.io.Source
import scala.concurrent.{Future, Promise}
import scala.concurrent.ExecutionContext.Implicits.global

class Grid(n: Int, solutionFilePath: String) {
  val width = 50
  val height = 50
  val random = new Random(11781400)

  val chars = Array('a', 'b', 'c', 'd', 'e', 'f')
  val numbers = Array.tabulate[Int](10){(i: Int) => i}
  var clusterToColor: Map[Int, String] = _
  val cellToCluster = Array.tabulate[Int](n*n){(i: Int) => i}

  def randomColor() : String = {
    var s = "#"
    for (i <- 0 until 6) {
      if (random.nextDouble < 0.5) {
        s += chars(random.nextInt(chars.length))
      } else {
        s += numbers(random.nextInt(numbers.length)).toString
      }
    }
    s
  }

  def parseFile(text: String) : Unit = {
    var firstLine = true
    for (line <- text.split("\n")) {
      val s = line.split(" ")
      if (firstLine) {
        firstLine = false
        clusterToColor = s map((elem: String) => elem.toInt -> randomColor()) toMap
      } else {
        cellToCluster(s(0).toInt) = s(1).toInt
      }
    }
  }

  def readTextFile(file: String) : Future[Either[DOMError, String]] = {
    val promisedErrorOrContent = Promise[Either[DOMError, String]]

    val reader = new FileReader()
      reader.readAsText(new dom.raw.Blob(js.Array(file)))

      reader.onload = (_: UIEvent) => {
        val resultAsString = s"${reader.result}"
        promisedErrorOrContent.success(Right(resultAsString))
      }
      reader.onerror = (_: Event) => promisedErrorOrContent.success(Left(reader.error))

      promisedErrorOrContent.future
  }

  val f = Ajax.get(solutionFilePath)
  f.onComplete {
    case Success(value) =>
      readTextFile(value.responseText).map {
        case Right(fileContent) => parseFile(fileContent); drawGrid()
        case Left(error) => println(s"Could not read file $solutionFilePath. Error: $error")
      }
    case Failure(e) => println(s"Failed to load file : $e")
  }


  def drawGrid() : Unit = {

   val gridData = new js.Array[js.Array[(Int, Int)]](n)
   for (i <- 0 until n) {
     gridData(i) = new js.Array[(Int, Int)](n)
   }

   for {
     i <- 0 until n
     j <- 0 until n
   } {
     gridData(i)(j) = (j*width, i*height)
   }

   val svg = d3.select("#grid").append("svg").attr("width", 2000).attr("height", 2000)
   
   val rows = svg.selectAll("row").data(gridData).enter().append("g").attr("class", "row").attr("width", 2000).attr("height", height)

   println(clusterToColor)
   println(cellToCluster.mkString(" "))

    val column = rows.selectAll("square")
      .data( (x: js.Array[(Int, Int)]) => x)
      .enter().append("rect")
      .attr("x", (i: (Int, Int)) => i._1)
      .attr("y", (i: (Int, Int)) => i._2)
      .attr("width", width)
      .attr("height", height)
      .style("fill", (i: (Int, Int)) => {
        val col = (i._1 / width)
        val row = (i._2 / height)
        val c = row*n + col
        clusterToColor(cellToCluster(c))
      })
      .style("stroke", "#222")
  }
}

object Grid {
  def apply(n: Int, f: String) = new Grid(n,f)
}
