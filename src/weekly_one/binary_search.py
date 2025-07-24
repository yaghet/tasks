def search(array: list[int], target: int) -> bool:

    left, right = 0, len(array) - 1

    while left < right:
        mid = (left + right) // 2

        if array[mid] == target:
            return True
        elif array[mid] > target:
            right = mid
        else:
            left = mid + 1

    return False


nums = [1, 2, 3, 45, 356, 569, 600, 705, 923]

if __name__ == '__main__':
    answer = search(nums, 46)
    print(answer)
