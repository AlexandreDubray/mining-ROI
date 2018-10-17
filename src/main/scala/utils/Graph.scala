package utils

import scala.io.Source
import scala.util.control.Breaks._

class Graph(val n: Int) {

  // adjacencyMatrix(i)(j) = flux from i to j
  val adjacencyMatrix = Array.fill[Int](n,n)(0)
  val inFlux = Array.fill[Int](n)(0)
  val clusters = UF(n)

  def link(node1: Int, node2: Int) : Unit = {
    adjacencyMatrix(node1)(node2) += 1
    inFlux(node2) += 1
  }

  def process(filepath: String) : Unit = {
    val buffer = Source.fromFile(filepath)
    for (line <- buffer.getLines) {
      val s = line.split(" ")
      link(s(0) toInt, s(1) toInt)
    }
    buffer.close

    for (i <- 0 until n) {
      inFlux(i) = adjacencyMatrix(i).reduceLeft(_ + _) max inFlux(i)
    }
  }

  def merge(repNode1: Int, repNode2: Int) : Unit = {
    // Merge node2 into node1
    // Update incoming flux
    inFlux(repNode1) = inFlux(repNode1) + inFlux(repNode2) - adjacencyMatrix(repNode1)(repNode2)
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
    var solutionFound = false
    while (!solutionFound && inFlux.reduceLeft(_ min _) < minFlux) {
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
          if ((adjacencyMatrix(n1)(n2) != 0 || adjacencyMatrix(n2)(n1) != 0) && (inFlux(n1) < minFlux || inFlux(n2) < minFlux)) {
            diffFlux match {
              case None => {
                diffFlux = Some(Math.abs(minFlux - (inFlux(n1) + inFlux(n2) - adjacencyMatrix(n1)(n2)) ))
                node1 = Some(n1)
                node2 = Some(n2)
              }
              case Some(value) => {
                val dFlux = Math.abs(minFlux - (inFlux(node1.get) + inFlux(node2.get) - adjacencyMatrix(node1.get)(node2.get)))
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
    println(Array.tabulate[Int](n){(i:Int) => i}.mkString(" "))
    println(clusters.id.mkString(" "))
    println("Incoming flux :")
    println(inFlux.mkString(" "))
  }
}

object Graph {

  def apply(n: Int) = new Graph(n)
  def apply(n: Int, filepath: String) = {
    val g = new Graph(n)
    g.process(filepath)
    g
  }
}
