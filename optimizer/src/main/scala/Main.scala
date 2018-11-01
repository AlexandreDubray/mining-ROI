import utils._

object Main {

  def main(args: Array[String]) : Unit = {
    val dataGen = DataGenerator(20,20)
    val trajectories = dataGen.generateTrajectories(200000, 5,15)
    dataGen.writeTrajectories("./optimizer/src/main/resources/fake-trajectories.in", trajectories)
    val g = Graph(20,20, "./optimizer/src/main/resources/fake-trajectories.in")
    g.optimize(20000)
    g.writeCluster("./webapp/src/main/resources/algo-output-fake.out")
    g.writeNewTrajectories("./optimizer/src/main/resources/fake-trajectories.in", "./webapp/src/main/resources/trajectories.out")
  }
}
