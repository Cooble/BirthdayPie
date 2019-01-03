
def toArray(string, max_length):#todo toarray doesn t work
    out = [""]
    spli = string.split(" ")
    for word in spli:
        if len(out[len(out) - 1]) + len(word) + 1 <= max_length:
            out[len(out) - 1] += " " + word
        else:
            out.append(word)
    out2 = []
    for i in range(len(out)):
        line = out[i]
        lineSplit = line.split("\n")
        if len(lineSplit) == 1:
            out2.append(line)
        else:
            for s in lineSplit:
                out2.append(s)

    for i in range(len(out2)):
        out2[i] = trim(out2[i])
    return out2
def trim(string):
    if string.startswith(" "):
        string = string[1:]
    if string.endswith(" "):
        string = string[:-1]
    return string
