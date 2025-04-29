import cs50

while True:
    try:
        height = cs50.get_int("Height: ")
        if height > 0 and height < 9:
            break
        else:
            pass
    except ValueError:
        pass

# Print the double pyramid
for i in range(1, height + 1):
    spaces = height - i
    hashes = i

    print(" " * spaces + "#" * hashes + "  " + "#" * hashes)