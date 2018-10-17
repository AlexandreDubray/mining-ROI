package utils

class UF(val n: Int) {

  val id: Array[Int] = Array.tabulate[Int](n){(i:Int) => i}
  val size: Array[Int] = Array.fill[Int](n)(1)
  var count: Int = n

  def union(p: Int, q: Int) : Int = {
    val i = find(p)
    val j = find(q)
    if (size(i) < size(j)) {
      id(i) = j
      size(j) += size(i)
      count -= 1
      j
    } else {
      id(j) = i
      size(i) += size(j)
      count -= 1
      i
    }
  }

  def find(p: Int) : Int = {
    var iter = p
    while (iter != id(iter))
      iter = id(iter)
    iter
  }

  def connected(p: Int, q: Int) : Boolean = {
    find(p) == find(q)
  }

}

object UF {
  def apply(n: Int) = new UF(n)
}
