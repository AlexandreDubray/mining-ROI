import sys

data_file = '../data/mip-matrix.tsv'
N = 0

def main():
    global N
    with open(data_file, 'r') as f:
        data = [[int(x) for x in line.split("\t")] for line in f.read().split("\n") if line != ""]
        maxX = -1
        minX = sys.maxsize
        maxY = -1
        minY = sys.maxsize
        for i in range(len(data)):
            for j in range(len(data)):
                if data[i][j] == 1:
                    maxX = max(maxX,j)
                    minX = min(minX,j)
                    maxY = max(maxY,i)
                    minY = min(minY,i)
                    N += 1

    data = data[minY:maxY+1]
    for i,d in enumerate(data):
        data[i] = d[minX:maxX+1]

    with open("./mip-sol.out", 'r') as f:
        bestK = None
        bestError = None
        bestLength = sys.maxsize
        rects = None
        for out in f.read().split('\n\n')[:-1]:

            covered = 0
            errored = 0

            s = out.split('\n')
            first = s[0]

            rs = s[1:]
            rss = [x.split(' ') for x in rs]
            re = [ (int(x), int(y), int(z), int(t)) for x,y,z,t in rss]

            for xmin, xmax, ymin, ymax in re:
                for col in range(xmin, xmax+1):
                    for row in range(ymin, ymax+1):
                        if data[row][col] == 1:
                            covered += 1
                        else:
                            errored += 1
            total_error_encode = (N - covered) + errored
            split = first.split(' ')
            K = int(split[0])
            if K + total_error_encode < bestLength:
                bestK = K
                bestError = total_error_encode
                bestLength = bestK + bestError
                rects = [x for x in re]
        with open(SCRIPT_DIR, '..', 'output', 'mip.out'), 'w') as f:
            for rect in rects:
                f.write('{}\n'.format(' '.join([str(x) for x in rect])))

if __name__ == '__main__':
    main()
