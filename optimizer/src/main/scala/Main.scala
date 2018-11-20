import utils.KDTree

import parser._

object Main {

  def prepareData() : String = {
    import java.nio.file.{Paths, Files}
    val parsedFilename = "KaggleTaxis"
    val filepath = "./data/parsed/" + parsedFilename + ".in"
    if (!Files.exists(Paths.get(filepath))) {
      val parser = KaggleParser()
      parser.parse(filepath)
    }
    filepath
  }

  def main(args: Array[String]) : Unit = {
    val dataFile = prepareData()
    val tree = KDTree(dataFile)
    tree.write_tree("./data/2D-tree.out")
  }
}
