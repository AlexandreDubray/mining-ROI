package webapp

import scala.scalajs.js

import org.scalajs.dom
import org.scalajs.dom._
import org.scalajs.dom.ext.Ajax

import scala.io.Source

import scala.util.{Success, Failure}

import scala.concurrent.{Future, Promise}
import scala.concurrent.ExecutionContext.Implicits.global

object IO {

  def parseFileContent(fileContent: String) : Array[Seq[(Double, Double)]] = {
    fileContent.split("\n").map( (p: String) => {
      val l = p.split(" ")
      val lowLat = l(0).toDouble
      val highLat = l(1).toDouble
      val lowLong = l(2).toDouble
      val highLong = l(3).toDouble
      Seq((lowLat, lowLong), (highLat, lowLong), (highLat, highLong), (lowLat, highLong))
    })
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

  def getData(file: String) : Future[Either[String,Array[Seq[(Double, Double)]]]] = {
    val promisedDataOrError = Promise[Either[String, Array[Seq[(Double, Double)]]]]
    val f = Ajax.get(file)
    f.onComplete {
      case Success(value) =>
        readTextFile(value.responseText).map {
          case Right(fileContent) => promisedDataOrError.success(Right(parseFileContent(fileContent)))
          case Left(error) => promisedDataOrError.success(Left(s"Could not read file $file. Error $error"))
        }
      case Failure(e) => promisedDataOrError.success(Left(s"Could not load file $file. Error $e"))
    }
    promisedDataOrError.future
  }
}
