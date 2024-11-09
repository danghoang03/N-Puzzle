import numpy as np
import random

def count_inversions(arr):
    inversions = 0
    flattened = [num for num in arr if num != 0]  # Bỏ ô trống
    for i in range(len(flattened)):
        for j in range(i + 1, len(flattened)):
            if flattened[i] > flattened[j]:
                inversions += 1
    return inversions

def is_solvable(puzzle, k):
    inversions = count_inversions(puzzle.flatten())
    if k % 2 == 1:
        # Kích thước lẻ: Số lần đảo vị phải là chẵn
        return inversions % 2 == 0
    else:
        # Kích thước chẵn: Số lần đảo vị và hàng của ô trống (từ dưới lên) phải có tổng là chẵn
        blank_row = np.where(puzzle == 0)[0][0]
        return (inversions + blank_row) % 2 == 1

def generate_puzzle(k):
    # Sinh ngẫu nhiên ma trận k x k và kiểm tra điều kiện giải được
    while True:
        puzzle = np.arange(k * k)
        np.random.shuffle(puzzle)
        puzzle = puzzle.reshape((k, k))
        if is_solvable(puzzle, k):
            return puzzle

# Ghi kết quả vào file với định dạng yêu cầu
def write_puzzle_to_file(puzzle, k, filename="input.txt"):
    with open(filename, "w") as f:
        f.write("1\n")  # Giá trị 1 cố định ở đầu file
        f.write(f"{k}\n")  # Ghi kích thước k
        for row in puzzle:
            f.write(" ".join(map(str, row)) + "\n")  # Ghi từng hàng của ma trận

# Yêu cầu người dùng nhập kích thước k
# k = int(input("Nhập kích thước ma trận (k x k): "))
# puzzle = generate_puzzle(k)
# write_puzzle_to_file(puzzle, k)
# print("Ma trận đã được ghi vào file input.txt.")
