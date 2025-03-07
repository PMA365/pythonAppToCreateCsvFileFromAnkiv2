import pathlib
import codecs
def main():
    substring = ""
    with open('testAnsware.html', 'r') as f:
        substring = f.read()
    # with open('testAnsware.txt', 'r', encoding='utf-8', errors='ignore') as f:
    #     substring = f.read(html)


    lastIndexOfpTag = substring.rfind("</p>")
    print(substring)
    if lastIndexOfpTag != -1:
        substring = substring[:lastIndexOfpTag]
        print(substring)


if __name__ == "__main__":
    main()