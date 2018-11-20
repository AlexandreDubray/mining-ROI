package webapp

import com.cibo.leaflet.{LatLng, Leaflet}
import scala.scalajs.js

import scala.concurrent.ExecutionContext.Implicits.global

object Webapp extends js.JSApp {

  import js.JSConverters._

  def main() : Unit = {
    val leafletMap = Leaflet.map("map").setView(LatLng(41.17, -8.6), 13)
    Leaflet
      .tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
      .addTo(leafletMap)

    IO.getData("./static/data/2D-tree.out").map {
      case Right(data:Array[Seq[(Double,Double)]]) => {
        data.foreach( (x: Seq[(Double, Double)]) => {
            val coords = x.map( (e:(Double, Double)) => LatLng(e._1, e._2)).toJSArray
            Leaflet.polygon(js.Array(coords)).addTo(leafletMap)
        })
      }
      case Left(error) => println(error)
    }
    
    /*
    val coords = Seq(
      LatLng(51.509, -0.08),
      LatLng(51.503, -0.06),
      LatLng(51.51, -0.047)
    ).toJSArray



    Leaflet.polygon(js.Array(coords)).addTo(leafletMap)
    */
  }
}
