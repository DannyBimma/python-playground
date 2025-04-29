import cs50

def main():
    text = cs50.get_string("Text: ")

    letters = count_letters(text)
    words = count_words(text)
    sentences = count_sentences(text)

    # Edge case for no words
    if words == 0:
        L = 0.0
        S = 0.0
    else:
        # Average number of letters per 100 words (L)
        L = (letters / words) * 100
        # Average number of sentences per 100 words (S)
        S = (sentences / words) * 100

    # Compute the Coleman-Liau index
    index = round(0.0588 * L - 0.296 * S - 15.8)

    # Print the grade level
    if index >= 16:
        print("Grade 16+")
    elif index < 1:
        print("Before Grade 1")
    else:
        print(f"Grade {index}")


def count_letters(text):
    letters = 0
    for char in text:
        if char.isalpha():
            letters += 1
    return letters

def count_words(text):
    words = len(text.split())
    return words

def count_sentences(text):
    sentences = 0
    for char in text:
        if char in ['.', '!', '?']:
            sentences += 1
    return sentences

if __name__ == "__main__":
    main()