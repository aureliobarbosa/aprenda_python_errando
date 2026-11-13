print("Oddify. Take a positive number and divide by 2 until it becomes odd!\n")


def oddify_number(n):

    result = [n]

    while True:  # condition for stopping the function
        if n % 2 == 0:  # even
            n = n // 2
            result.append(n)
        else:  # odd
            break

    return result


n = int(input("Enter a number to oddify: "))
x = oddify_number(n)

print(x)
