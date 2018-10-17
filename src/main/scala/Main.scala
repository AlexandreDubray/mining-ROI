import utils._

object Main {

  def main(args: Array[String]) : Unit = {
    //val testfile = "../Resources/data-test.in"
    val testfile = "./src/main/resources/data-test.in"
    val nNodes = 19
    val g = Graph(nNodes, testfile)
    println("Optimizing graph for minCover 2")
    g.optimize(2)
  }
}
