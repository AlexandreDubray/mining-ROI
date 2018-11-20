import scala.sys.process._

name := "master-thesis-code"
version := "0.1"
scalaVersion := "2.12.6"

libraryDependencies += "org.scalactic" %% "scalactic" % "3.0.5"
libraryDependencies += "org.scalatest" %% "scalatest" % "3.0.5" % "test"

addCommandAlias("rebuild", Seq("optimizer/run", "webapp/fastOptJS",
"copyDataScript").mkString(";",";",""))

lazy val copyDataScript = taskKey[Unit]("Copying data to webapp folder")

copyDataScript := {
    "cp ./data/2D-tree.out ./webapp/src/main/resources/static/data"!
}

lazy val optimizer = project
    .in(file("optimizer"))
    .dependsOn(parser)

lazy val webapp = project
    .in(file("webapp"))
    .settings(
        scalaJSUseMainModuleInitializer := true,
        resolvers += Resolver.bintrayRepo("cibotech", "public"),
        libraryDependencies += "com.cibo" %%% "leaflet-facade" % "1.0.3"
    ).enablePlugins(ScalaJSPlugin)

lazy val parser = project
    .in(file("parser"))
