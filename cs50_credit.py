def main():
    # Get card number input and print validation result
    while True:
        try:
            card_num = input("Number: ")
            
            if not card_num.isdigit():
                print("Please enter only digits.")
                continue
            else:
                break
        except ValueError:
            pass

    if not luhns_algo(card_num):
        print("INVALID")
    else:
        card_type = card_checker(card_num)
        print(card_type)


def luhns_algo(card_num_str: str) -> bool:
    num_sum = 0
    num_len = len(card_num_str)
    
    # Loop over every other digit starting from the second-to-last digit
    for i in range(num_len - 2, -1, -2):
        digit = int(card_num_str[i]) * 2
        num_sum += (digit % 10) + (digit // 10)

    # Loop over every other digit starting from the last digit
    for i in range(num_len - 1, -1, -2):
        num_sum += int(card_num_str[i])

    return num_sum % 10 == 0

def card_checker(card_num_str: str) -> str:
    num_len = len(card_num_str)

    # AMEX: 15 digits, starts with 34 or 37
    if num_len == 15 and card_num_str.startswith(("34", "37")):
        return "AMEX"
    
    # MASTERCARD: 16 digits, starts with 51, 52, 53, 54, or 55
    if num_len == 16 and card_num_str.startswith(("51", "52", "53", "54", "55")):
        return "MASTERCARD"

    # VISA: 13 or 16 digits, starts with 4
    if (num_len == 13 or num_len == 16) and card_num_str.startswith("4"):
        return "VISA"

    return "INVALID"


if __name__ == "__main__":
    main()