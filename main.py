# program to convert anki v2 files to .csv format
# C:\Users\hp 2570p\Documents\1100 tofel words\1100 NB Barrons-ENGLISH to PERSIAN(farsi) v4.4_[images]+G+D.apkg

import re
import sys
import sqlite3
import os
import zipfile
import pathlib
import pandas as pd
def answare_creator(row) :
    substring =""
    # need to find the first occurrence of rtl and sunstring whole after
    # first we need to find the last #007000 occur:
    lastIndexOfkeyTag = row.rfind("#007000")
    if lastIndexOfkeyTag != -1:
        substring = row[lastIndexOfkeyTag:]
        substring = row.replace(row[:lastIndexOfkeyTag], "")
        
 
        firstOccurrencesOfRTLindex = row.find("rtl\">") 
        substring = row[firstOccurrencesOfRTLindex+5:] # delete first part till rtl index

        
    
    lastIndexOfpTag = substring.rfind("</p>")
    if lastIndexOfpTag != -1:
        substring = substring[:lastIndexOfpTag]

    lastIndexOfspanTag = substring.rfind("</span>")
    if lastIndexOfspanTag != -1:
        substring= substring[:lastIndexOfspanTag]

    # between ▼ ▼ is mp3 and need to be deleted
    # Find the substring between two ▼ characters and delete it
    substring = re.sub(r'▼.*?▼', '', substring)
    #remove mp3
    substring = re.sub(r'.\d-D\d_\d+\.mp3', '', substring)
    substring = re.sub(r'▼▼.*?▼', '', substring)
    # some musics are between [ ] tags
    substring = re.sub(r'\[.*?\]', '', substring)
    # removing all html tags
    # Remove HTML tags
    substring = re.sub(r'<.*?>', '', substring)

    # Remove HTML entities
    substring = re.sub(r'&[^;]*;', '', substring)

    # Remove extra whitespace
    substring = re.sub(r'\s+', ' ', substring)

    
    # substring = re.sub(r'<[^>]*>|<\/[^>]*>', '', substring)
    # substring = substring.replace("<(.*?)>|<\/(.*?)>", "");
    if len(substring) < 30 :
        substring = ""
    return substring
def find_first_two_occurrences(string , word):
    indices = []
    index = string.find(word)
    while index != -1:
        indices.append(index)
        index = string.find(word, index + 1)
    return indices[:2]

def find_last_two_occurrences(string, word):
    indices = []
    index = string.find(word)
    while index != -1:
        indices.append(index)
        index = string.find(word, index + 1)
    return indices[-2:]

def find_all_occurrences(string, word):
    indices = []
    index = string.find(word)
    while index != -1:
        indices.append(index)
        index = string.find(word, index + 1)
    return indices

def question_creator(row) :
    substring =""
    word = "big>"
    indices = find_last_two_occurrences(row, word)
    # Substring the string between the two indexes
    if len(indices) == 2:
        # finding the Question word
        substring = row[indices[0]:indices[1] + len(word)]
        # cleaning any redundant tags from it such as sup tags
        supIndices = find_all_occurrences(substring, "sup>")
        if len(supIndices) >= 2:
            # string.replace(string[start:end], "") deleting the sup tag
            substring = substring[:supIndices[0]] + substring[supIndices[-1] + len("sup>"):]

        substring = substring[:-9] # delete last 9 characters
        substring = substring[7:] # delete first 7 characters
        substring = substring.replace("<", "") # delete every < characters

    else :
        #method 2 of finding the word of question
        # our jey is #000000 occures right before the Word
        lastIndexOfkeyTag = row.rfind("#007000")
        if lastIndexOfkeyTag != -1:
            substring = row[lastIndexOfkeyTag:]
            substring = row.replace(row[:lastIndexOfkeyTag+2], "")

        bTagIndices = find_first_two_occurrences(row,"b>")
        if len(bTagIndices) == 2: 
            substring = row[bTagIndices[0]:bTagIndices[1] + len("b>")]
            print(substring)
            substring = substring[:-4] # delete last 9 characters
            substring = substring[2:] # delete first 7 characters
            print(substring)
            print("\n \n")

    return substring

def get_file_path_from_user():
    file_path = input("Please enter the complete file path: ")
    if os.path.exists(file_path):
        print("You entered: ", file_path)
        print("successful")
        return file_path
    else:
        print("File not found. Please try again.")

def main():
    anki21 = False
    # Define the path to the file you want to extract
    file_to_extract = get_file_path_from_user() #'path/to/your/file.zip'

    # Define the path to the folder where you want to extract the files
    extract_folder = 'yourAnkiFileDatabaseHere'

    # Define the specific data file you want to keep
    files_to_keep = []
    file_path = pathlib.Path(file_to_extract)


    # check if can read the file or not
    if os.access(file_path , os.R_OK) == False:
        print(f"Permission denied: cannot read from {file_path}")
        sys.exit(1)

    # Extract the file
    
    with zipfile.ZipFile(file_to_extract, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)


    # Get a list of all files in the extract folder
    files_in_folder = os.listdir(extract_folder)

    # Keep only the specific data file
    for file in os.listdir(extract_folder):
        if file.endswith('.anki21') or file.endswith('.anki2'):
            files_to_keep.append(file)
    for file in os.listdir(extract_folder):
        if file not in files_to_keep:
            os.remove(os.path.join(extract_folder, file))
    
    if len(files_to_keep) > 1:
        files_to_keep = [file for file in files_to_keep if file.endswith('.anki21')]
        anki21 = True

    # Connect to the SQLite database
    db_path = os.path.join(extract_folder, files_to_keep[0])
    conn = sqlite3.connect(db_path)    
    
    # Create a cursor object
    cur = conn.cursor()

    # Execute a query
    # Specify the table and column names
    table_name = 'notes'
    column_name = 'flds'

    # Execute the query
    cur.execute(f"SELECT {column_name} FROM {table_name}")

    # Fetch all rows
    rows = cur.fetchall()

    print(len(rows))


    # Create an empty DataFrame with 2 columns
    df = pd.DataFrame(columns=['Question', 'Answare'])
    i = 0
    while i < len(rows):
    # while i < 2:

        question = question_creator(rows[i][0]) 
        # print(question)
        # answare = input("Enter value for Column2: ")
        answare = answare_creator(rows[i][0])
        # print(answare)
        # print("\n\n")
        # Add the data to the DataFrame
        df.loc[len(df.index)] = [question, answare]

        i+=1

    # print(df)
    output_dir = os.path.join(os.getcwd(), 'Output')
    df.to_csv(os.path.join(output_dir, 'output.csv'), index=False)
    # Print the rows
    # for row in rows:
        # print(row[0])

    # Close the connection
    conn.close()


if __name__ == "__main__":
    main()