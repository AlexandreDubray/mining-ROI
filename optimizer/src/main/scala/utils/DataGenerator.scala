package utils

import scala.util.Random
import scala.collection.immutable.ListMap

class DataGenerator(val height: Int, val width: Int) {
  val n = height*width

  val random = new Random(11781400)

  def generatePI(number: Int) : Seq[Int] = Array.tabulate[Int](number) { (i:Int) => random.nextInt(n); } distinct

  val interestPoints = generatePI(10)
  val numberPI = interestPoints.length

  def selectDestPI() : Int = interestPoints(random.nextInt(numberPI))

  def getCellsInSquare(minCol: Int, maxCol: Int, minRow: Int, maxRow: Int) : Seq[Int] = {
    val nbCol = (maxCol - minCol + 1)
    val nbRow = (maxRow - minRow + 1)
    val nbCell = nbCol*nbRow
    Array.tabulate[Int](nbCell) { (i: Int) => 
      val curRow = minRow + (i / nbCol)
      val curCol = minCol + (i % nbCol)
      curRow*width + curCol
    }
  }

  def generateTrajectory(length: Int) : Seq[Int] = {
    val startCell = random.nextInt(n)
    val startRow = startCell / width
    val startCol = startCell % width

    val endCell = selectDestPI
    val endRow = endCell / width
    val endCol = endCell % width

    if (startCol < endCol) {
      if (startRow < endRow) {
        for {
          i <- startRow to endRow
          j <- startCol to endCol
        } yield i*width + j
      } else {
        for {
          i <- startRow to endRow by -1
          j <- startCol to endCol
        } yield i*width + j
      }
    } else {
      if (startRow < endRow) {
        for {
          i <- startRow to endRow
          j <- startCol to endCol by -1
        } yield i*width + j
      } else {
        for {
          i <- startRow to endRow by -1
          j <- startCol to endCol by -1
        } yield i*width + j
      }
    }
  }

  def generateTrajectories(number: Int, minLength: Int, maxLength: Int) : Seq[Seq[Int]] = {
    Array.tabulate[Seq[Int]](number){ (i: Int) =>
      val length = random.nextInt(maxLength - minLength + 1) + minLength
      generateTrajectory(length)
    }
  }

  def writeTrajectories(filepath: String, trajectories: Seq[Seq[Int]]) : Unit = {
    import java.io.PrintWriter
    println("Interest point : ")
    println(interestPoints.mkString(" "))
    new PrintWriter(filepath) {
      trajectories.foreach( (i:Seq[Int]) => {
        write(i.mkString(" "))
        write("\n")
      })
      close
    }
  }
}

object DataGenerator {
  def apply(height: Int, width: Int) = new DataGenerator(height, width)
}
