name := "master-thesis-code"
version := "0.1"
scalaVersion := "2.12.6"

libraryDependencies += "org.scalactic" %% "scalactic" % "3.0.5"
libraryDependencies += "org.scalatest" %% "scalatest" % "3.0.5" % "test"

lazy val optimizer = project.in(file("optimizer"))
lazy val webapp = project
    .in(file("webapp"))
    .settings(
        scalaJSUseMainModuleInitializer := true,
        libraryDependencies += "org.singlespaced" %%% "scalajs-d3" % "0.3.4",
        libraryDependencies += "org.scala-js" %%% "scalajs-dom" % "0.9.6"
    ).enablePlugins(ScalaJSPlugin)
