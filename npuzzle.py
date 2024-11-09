from queue import LifoQueue
from time import time

class State:
    def __init__(self, state, parent, action, depth, size):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.size = size
        # Goal state: [1,2,...,k*k - 1,0]
        self.goal = list(range(1, size * size)) + [0]
        
    def check(self):
        # Kiểm tra trạng thái hiện tại có phải là trạng thái mục tiêu hay chưa
        return self.state == self.goal
    
    # Xác định các hành động di chuyển hợp lệ cho trạng thái hiện tại
    def available_moves(self, x): 
        moves = ['Left', 'Right', 'Up', 'Down']
        size = self.size
        # Ô trống không thể đi sang trái
        if x % size == 0:
            moves.remove('Left')
        # Ô trống không thể đi sang phải
        if x % size == size - 1:
            moves.remove('Right')
        # Ô trống không thể đi lên trên
        if x - size < 0:
            moves.remove('Up')
        # Ô trống không thể đi xuống dưới
        if x + size >= size * size:
            moves.remove('Down')
            
        # Loại bỏ hành động ngược lại hành động cha
        if self.action == 'Left' and 'Right' in moves:
            moves.remove('Right')
        elif self.action == 'Right' and 'Left' in moves:
            moves.remove('Left')
        elif self.action == 'Up' and 'Down' in moves:
            moves.remove('Down')
        elif self.action == 'Down' and 'Up' in moves:
            moves.remove('Up')
            
        return moves
    
    # Sinh ra các node con từ trạng thái hiện tại
    def expand(self):
        x = self.state.index(0) # Tìm vị trí của ô trống (0) của trạng thái hiện tại
        moves = self.available_moves(x) # Lấy danh sách các hành động hợp lệ cho trạng thái hiện tại
        children = [] # Danh sách chứa các trạng thái được sinh ra từ trạng thái hiện tại
        
        for action in moves:
            temp = self.state.copy() # Tạo bản sao của trạng thái hiện tại
            
            # Di chuyển các ô trống theo hành động tương ứng
            if action == 'Left':
                temp[x], temp[x - 1] = temp[x - 1], temp[x]
            elif action == 'Right':
                temp[x], temp[x + 1] = temp[x + 1], temp[x]
            elif action == 'Up':
                temp[x], temp[x - self.size] = temp[x - self.size], temp[x]
            elif action == 'Down':
                temp[x], temp[x + self.size] = temp[x + self.size], temp[x]
            
            # Tạo node con từ trạng thái đã được di chuyển
            child = State(temp, self, action, self.depth + 1, self.size)
            children.append(child)
        
        return children
    
    # Hàm trả về lời giải
    def solution(self):
        solution = []
        path = self
        while path.parent is not None:
            solution.append(path.action)
            path = path.parent
        solution.reverse()
        return solution
    

# Hàm thực hiện giải thuật DFS
def DFS(given_state, size):
    # Khởi tạo nút gốc
    root = State(given_state, None, None, 0, size)
        
    # Kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu hay không, nếu phải thì trả về lời giải bài toán
    if root.check():
        return root.solution(), 0
        
    # Tạo ngăn xếp (stack) cho các nút sẽ duyệt
    stack = [root]
    visited = set()    
        
    # Duyệt qua stack
    while stack:
        current_node = stack.pop()
        if current_node.check():
            return current_node.solution(), len(visited)
        state_hash = hash(tuple(current_node.state))
        visited.add(state_hash)
        
        # Tạo các nút con
        children = current_node.expand() 
        
        for child in children:
            child_hash = hash(tuple(child.state))
            #kiểm tra xem nút này đã duyệt hay chưa, nếu chưa thì thêm vào stack
            if child_hash not in visited:
                stack.append(child)
    
    #trả về không tìm thấy lời giải và số nút đã duyệt  
    return None, len(visited)

def DFS_with_steps(given_state, size, solution_queue):
    """
    Giải thuật DFS nhưng gửi các bước di chuyển qua Queue khi tìm thấy lời giải.
    """
    # Khởi tạo nút gốc
    root = State(given_state, None, None, 0, size)
        
    # Kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu hay không, nếu phải thì trả về lời giải bài toán
    if root.check():
        solution = root.solution()
        for step in solution:
            solution_queue.put(step)
        solution_queue.put("DONE")
        return 0, 0
        
    # Tạo ngăn xếp (stack) cho các nút sẽ duyệt
    stack = [root]
    visited = set()   
    nodes_visited = 0 
    start_time = time()
    solution = []
        
    # Duyệt qua stack
    while stack:
        current_node = stack.pop()
        nodes_visited += 1

        if current_node.check():
            solution = current_node.solution()
            for step in solution:
                solution_queue.put(step)
            solution_queue.put("DONE")
            elapsed_time = time() - start_time
            solution.append(solution)
            return elapsed_time, nodes_visited, len(solution) - 1
        
        state_hash = hash(tuple(current_node.state))
        visited.add(state_hash)
        
        # Tạo các nút con
        children = current_node.expand() 
        
        for child in children:
            child_hash = hash(tuple(child.state))
            #kiểm tra xem nút này đã duyệt hay chưa, nếu chưa thì thêm vào stack
            if child_hash not in visited:
                stack.append(child)
    
    #trả về không tìm thấy lời giải và số nút đã duyệt 
    solution_queue.put("DONE")
    elapsed_time = time() - start_time 
    return None, elapsed_time, nodes_visited, len(solution) - 1

# Hàm hiện thực giải thuật DLS (Giải thuật DFS có giới hạn độ sâu tìm kiếm)
def DLS(given_state, size, max_depth):
    # Khởi tạo nút gốc
    root = State(given_state, None, None, 0, size)
        
    # Kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu hay không, nếu phải thì trả về lời giải bài toán
    if root.check():
        return root.solution(), 0
        
    # Tạo ngăn xếp (stack) cho các nút sẽ duyệt
    stack = [root]
    visited = set()    
        
    # Duyệt qua stack
    while stack:
        current_node = stack.pop()
        if current_node.check():
            return current_node.solution(), len(visited)
        depth = current_node.depth 
        state_hash = hash(tuple(current_node.state))
        visited.add(state_hash)
        
        if depth >= max_depth:
            continue
        
        # Tạo các nút con
        children = current_node.expand() 
        
        for child in children:
            child_hash = hash(tuple(child.state))
            #kiểm tra xem nút này đã duyệt hay chưa, nếu chưa thì thêm vào stack
            if child_hash not in visited:
                stack.append(child)
    
    #trả về không tìm thấy lời giải và số nút đã duyệt  
    return None, len(visited)

# Hàm thực hiện giải thuật IDS (Iterative Deepening Search cải tiến từ DLS)
def IDS(given_state, size, max_depth):
    # Tăng độ sâu tìm kiếm từ 1 -> max_depth
    for depth in range(1 ,max_depth + 1):
        solution, nodes_visited = DLS(given_state, size, depth)
        # Nếu tại độ sâu depth có lời giải bài toán, trả về lời giải đó và kết thúc hàm
        if solution is not None:
            return solution, nodes_visited
    return None, nodes_visited

def IDS_with_steps(given_state, size, max_depth, solution_queue):
    """
    Giải thuật IDS nhưng gửi các bước di chuyển qua Queue khi tìm thấy lời giải.
    """
    start_time = time()
    total_nodes_visited = 0
    solution = []

    for depth in range(1, max_depth + 1):
        solution, nodes_visited = DLS(given_state, size, depth)
        total_nodes_visited += nodes_visited
        if solution is not None:
            # Gửi từng bước di chuyển qua Queue
            for step in solution:
                solution_queue.put(step)
            solution_queue.put("DONE")
            elapsed_time = time() - start_time
            solution.append(solution)
            return elapsed_time, total_nodes_visited, len(solution) - 1
    
    solution_queue.put("DONE")
    elapsed_time = time() - start_time
    return elapsed_time, total_nodes_visited, len(solution) - 1


def readInput(filename):
    with open(filename, "r") as file:
        inputs = []
        numInput = int(file.readline().strip())
        for _ in range(numInput):
            state = []
            size = int(file.readline().strip())
            for _ in range(size):
                row = list(map(int, file.readline().strip().split()))
                state.extend(row)
            inputs.append((size, state))
            
    return inputs


def writeOutput(filename, solutions):
    with open(filename, 'w') as file:
        for solution, nodes_visited, elapsed_time in solutions:
            file.write(f"Action: {solution}\n")
            file.write(f"Number of explored nodes is: {nodes_visited}\n")
            file.write(f"Time: {elapsed_time:.4f} second")
    
def main():
    # Đọc bài toán từ file input
    inputs = readInput("input.txt")
    output_file = "output.txt"
    print("Loading...")
    solutions = []
    for size, initial_state in inputs:
        start_time = time()
        # solution, nodes_visited = DFS(initial_state, size)
        solution, nodes_visited = IDS(initial_state, size, 80)
        elapsed_time = time() - start_time
        solutions.append((solution, nodes_visited, elapsed_time))
        print("Solution:", solution)

    writeOutput(output_file, solutions)
    print("Done!")

if __name__ == "__main__":
    main()
