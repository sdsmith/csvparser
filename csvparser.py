#!/usr/bin/python2.7
"""
csvparser.py

Writer takes any list or rows and converts it to a csv file format.
Reader takes the writer's output file and converts it back to the original list.
"""

DEBUG = False



class Dialect:
    delimiter = None
    escapechar = None
    lineterminator = None
    quotechar = None
    
    def __init__(self, delimiter, escapechar, lineterminator, quotechar):
        self.delimiter = delimiter
        self.escapechar = escapechar
        self.lineterminator = lineterminator
        self.quotechar = quotechar


def printd(string):
    if (DEBUG):
        print(string)


class Writer:
    _dialect = None
    _file = None

    """
    outfile     open file object
    """
    def __init__(self, outfile, delimiter = ",", escapechar = "\\", lineterminator = "\r\n", quotechar = '"'):
        self._dialect = Dialect(delimiter, escapechar, lineterminator, quotechar)
        self._file = outfile


    """
    Writes each item of the given list 'row' to the file after formatting.
    row         list object
    """
    def writerow(self, row):
        len_row = len(row)
        
        for i in range(0, len_row):
            # add delimiter if it is not the last item in row
            printd("row[{0}] = {1}".format(i, str(row[i])))
            self._file.write(self.formatStringToCSV(row[i], (i != len_row-1)))


    """
    Formats the given string to have the dialects quotechar at the start and end of the string.
    Escapes any quotechar, delimiter, or escapsechar with the escape char. Replcases all newlines
    ("\r\n" or "\n") with lineterminator. Keeps whitesapce as is.
    """
    def formatStringToCSV(self, string, addDelimiter):
        # add starting quote character
        formattedString = self._dialect.quotechar
        string = str(string)
        len_string = len(string)
        
        skipiteration = False
        
        for i in range(0, len_string):
            printd("formattedString = %s" % formattedString)
            printd("char = %s" % string[i])
            if (skipiteration):
                skipiteration = False
                continue
            
            if string[i] == "\r":
                # check for \r\n
                printd("\t\\r found, check if it's \\r\\n")
                if i != len_string - 1: # Avoids index out of range error
                    if string[i+1] == "\n":
                        printd("\t\t\\r\\n confirmed")
                        formattedString = formattedString + self._dialect.lineterminator
                        skipiteration = True
                        continue   # skip an iteration of the loop

                # if out of range or the loop didn't hit 'continue', just add the charcater
                formattedString = formattedString + string[i]

                
            elif string[i] == "\n":
                # check for \n
                printd("\t\\n found")
                formattedString = formattedString + self._dialect.lineterminator

            elif string[i] in [self._dialect.delimiter, self._dialect.escapechar, self._dialect.quotechar]:
                # check for delimiter, excapechar, or quotechar
                printd("\tescape charcter needed")
                formattedString = formattedString + self._dialect.escapechar + string[i]

            else:
                # add character
                printd("\tadding character to string")
                formattedString = formattedString + string[i]

            printd("\n")

        # add the final quote char
        printd("formattedString = %s" % formattedString)
        printd("adding final quotechar")
        formattedString = formattedString + self._dialect.quotechar

        if (addDelimiter):
            # add delimiter at the end of the string
            printd("adding delimiter")
            formattedString = formattedString + self._dialect.delimiter
        else:
            # add newline to the end of the file if there is no delimiter
            printd("adding lineterminator")
            formattedString = formattedString + self._dialect.lineterminator
        
        printd("formattedString = %s" % formattedString)
        return formattedString


class Reader:
    _dialect = None
    _csvfile = None
    char = None     # current char in file

    """
    csvfile     open file object
    """
    def __init__(self, csvfile, delimiter = ",", escapechar = "\\", lineterminator = "\r\n", quotechar = '"'):
        self._dialect = Dialect(delimiter, escapechar, lineterminator, quotechar)
        self._csvfile = csvfile


    """
    Read a single row of the file.
    """
    def readrow(self):
        row = []    # list of string items to be returned


        # find the start of the first row (should be the first character)
        while (self.char != self._dialect.quotechar):
            self.char = self._csvfile.read(1)

            # check EOF
            if not self.char:
                return None

        # add item to row
        row.append(self.getStringItem())

        # continue checking row
        while (1):
            # check for delimiter, start of new row, or EOF
            self.char = self._csvfile.read(1)

            # check EOF
            if not self.char:
                return None
            
            if self.char == self._dialect.delimiter:
                # get to the next quote and append the next item to the row
                self._csvfile.read(1)           # skip to the next quotechar
                row.append(self.getStringItem())
                
            else:
                # no delimiter, end of row
                break

        return row



    """
    Assumes that the first quotechar has been found and searches for the second quotechar to end the item.
    """
    def getStringItem(self):
        strItem = ""   # string representation of the current item
        foundEndQuote = False

        # must be called with file pointer on the starting quotechar
#        if self.char != self._dialect.quotechar:
#            raise Exception
        
        # start item
        while not foundEndQuote:
            self.char = self._csvfile.read(1)

            # check for end of string
            if self.char == self._dialect.quotechar:
                # end while
                foundEndQuote = True

            # check the escape character
            elif self.char == self._dialect.escapechar:
                # take the next character, add it to string
                self.char = self._csvfile.read(1)
                strItem = strItem + self.char

            # add current character
            else:
                strItem = strItem + self.char
        # end item

        return strItem


if __name__ == "__main__":
    print("Starting write")
    
    csvfile = open("data.csv", "wb")
    w = Writer(csvfile)
    w.writerow([1, 1, "this is a test file. trying to test things like \\ and1 \" and2 \n and3 \r\n. test complete. print(\"This is a print statement\")"])
    w.writerow([2, 2, "this is the second row\n"])
    w.writerow([334493, 404, " }   }   System.out.println(currentRoom.longDescription()); to go...ismann Gymnasium.\");me.\");"])
    csvfile.close()
    print("done")
    
    print("Starting read")

    csvfile = open("data.csv", "rb")
    r = Reader(csvfile)
    row = r.readrow()
    while (row != None):
        print(row)
        row = r.readrow()
    csvfile.close()
    print("done")

    print("\nStarting read of Blackbox content")
    csvfile = open("content_test1.csv", "rb")
    r = Reader(csvfile)
    row = r.readrow()

    while (row != None):
        print(row)
        row = r.readrow()
    csvfile.close()
    print("done")

    import traceback

    print(''.join(traceback.format_stack()))
        




    

    
