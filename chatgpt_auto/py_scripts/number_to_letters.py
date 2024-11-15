# number_to_letters.py
import inflect

def number_to_letters(num):
    p = inflect.engine()
    return p.number_to_words(num)

def main():
    num = int(input("Enter a number: "))
    print(number_to_letters(num))

if __name__ == '__main__':
    main()