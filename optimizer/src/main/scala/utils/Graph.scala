package utils

import scala.io.Source

// class representing the graph of a height by width grid
class Graph(val height: Int, val width: Int) {

  val n = height*width
  // adjacencyMatrix(i)(j) = flux from i to j
  val adjacencyMatrix = Array.fill[Int](n,n)(0)
  val inFlux = Array.fill[Int](n)(0)
  val clusters = UF(n)
  
  val neighbour = Array.tabulate[Set[Int]](n){ i =>
    val row = i / height
    val col = i % height
    val cell = row*height + col
    var set: Set[Int] = Set()

    val uN = cell - width
    val dN = cell + width
    val lN = cell - 1
    val rN = cell + 1
    if (row == 0) {
      set += dN
    } else if (row == height - 1) {
      set += uN
    } else {
      set ++= Set(uN, dN)
    }

    if (col == 0) {
      set += rN
    } else if (col == width -1) {
      set += lN
    } else {
      set ++= Set(lN, rN)
    }
    set
  }

  def link(node1: Int, node2: Int) : Unit = {
    adjacencyMatrix(node1)(node2) += 1
    inFlux(node2) += 1
  }

  def process(filepath: String) : Unit = {
    val buffer = Source.fromFile(filepath)
    for (line <- buffer.getLines) {
      val s = line.split(" ")
      for (i <- 0 until s.length - 1)
        link(s(i) toInt, s(i+1) toInt)
    }
    buffer.close

    for (i <- 0 until n) {
      inFlux(i) = adjacencyMatrix(i).reduceLeft(_ + _) max inFlux(i)
    }
  }

  def merge(repNode1: Int, repNode2: Int) : Unit = {
    // Merge node2 into node1
    // Update incoming flux
    inFlux(repNode1) = (inFlux(repNode1) - adjacencyMatrix(repNode2)(repNode1)) + (inFlux(repNode2) - adjacencyMatrix(repNode1)(repNode2))

    neighbour(repNode1) ++= neighbour(repNode2)

    clusters.union(repNode1, repNode2)
    for (i <- 0 until n) {
      if (i != repNode1) {
        // Redirecting flux from i to node1
        adjacencyMatrix(i)(repNode1) += adjacencyMatrix(i)(repNode2)
      }
      // Deleting link between i and node2
      adjacencyMatrix(i)(repNode2) = 0
      if (i != repNode1) {
        // Redirecting outgoing flux from node2 to i
        adjacencyMatrix(repNode1)(i) += adjacencyMatrix(repNode2)(i)
      }
      adjacencyMatrix(repNode2)(i) = 0
    }
  }

  def optimize(minFlux: Int) : Unit = {
    // Merging all node that have 0 inFlux together
    var firstZeroNode: Option[Int] = None
    (0 until n).foreach { i =>
      if (inFlux(i) == 0) {
        firstZeroNode match {
          case None => firstZeroNode = Some(i)
          case Some(value) => merge(value, i)
        }
      }
    }

    var solutionFound = false
    while (!solutionFound && inFlux(clusters.id.reduceLeft((i:Int, j: Int) => {
      if (inFlux(i) < inFlux(j))
        i
      else
        j
    })) < minFlux) {
      var node1: Option[Int] = None
      var node2: Option[Int] = None
      var diffFlux: Option[Int] = None

      for {
        i <- 0 until n
        j <- 0 until n
        // We consider node not merge together already
        if !clusters.connected(i,j)
        } {
          val n1 = clusters.find(i)
          val n2 = clusters.find(j)
          // We only want to merge cluster connected between them
          if ((adjacencyMatrix(n1)(n2) != 0 || adjacencyMatrix(n2)(n1) != 0) && (inFlux(n1) < minFlux || inFlux(n2) < minFlux) && neighbour(n1).contains(n2)) {
            diffFlux match {
              case None => {
                val newFlux = (inFlux(n1) - adjacencyMatrix(n2)(n1)) + (inFlux(n2) - adjacencyMatrix(n1)(n2))
                diffFlux = Some(Math.abs(minFlux - newFlux))
                node1 = Some(n1)
                node2 = Some(n2)
              }
              case Some(value) => {
                val newFlux = (inFlux(node1.get) - adjacencyMatrix(node2.get)(node1.get)) + (inFlux(node2.get) - adjacencyMatrix(node1.get)(node2.get))
                val dFlux = Math.abs(minFlux - newFlux)
                if (dFlux < value) {
                  diffFlux = Some(dFlux)
                  node1 = Some(n1)
                  node2 = Some(n2)
                }
              }
            }
          }
        }

        node1 match {
          case None => solutionFound = true
          case Some(i) => {
            merge(node1.get, node2.get)
          }
        }
    }
    println(s"Number of cluster: ${clusters.count}")
    //println(Array.tabulate[Int](n){(i:Int) => i}.mkString(" "))
    println(clusters.id.groupBy(identity).keys.toList.mkString(" "))
  }

  def writeCluster(filepath: String) : Unit = {
    import java.io.PrintWriter
    new PrintWriter(filepath) {
      println(clusters.id.distinct.mkString(" "))
      clusters.id.zipWithIndex.sortBy(x => (x._1, x._2)).foreach( (x:(Int,Int)) => {
        println(s"${x._2} ${clusters.id(x._2)}")
      })
      close;
    }
  }

  def writeNewTrajectories(initialTrajectoryPath: String, filepath: String) : Unit = {
    import java.io.PrintWriter
    new PrintWriter(filepath) {
      val buffer = Source.fromFile(initialTrajectoryPath)
      for (line <- buffer.getLines) {
        var prev = -1
        for (c <- line.split(" ")) {
          if (clusters.id(c.toInt) != prev) {
            prev = clusters.id(c.toInt)
            print(clusters.id(c toInt))
            print(" ")
          }
        }
        print("\n")
      }
      close;
    }
  }
}

object Graph {

  def apply(n: Int) = new Graph(n,n)
  def apply(n: Int, filepath: String) = {
    val g = new Graph(n,n)
    g.process(filepath)
    g
  }
  def apply(n: Int, k: Int) = new Graph(n,k)
  def apply(n: Int, k: Int, filepath: String) = {
    val g = new Graph(n,k)
    g.process(filepath)
    g
  }
}
