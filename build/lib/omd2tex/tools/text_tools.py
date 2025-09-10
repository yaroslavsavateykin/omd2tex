import re


def remove_elements(lst, elem):
    return [item for item in lst if item != elem]


def return_func(string, elem, func):
    string = "".join(string).split(elem)  # .strip().split(elem)

    if string[0] == "":
        string = remove_elements(string, "")
        if len(string) == 1:
            N = 1
        else:
            N = int(len(string) / 2)
        for i in range(N):
            j = 2 * i
            string[j] = func(string[j])

    else:
        string = remove_elements(string, "")
        N = int(len(string) / 2)
        for i in range(N):
            j = 2 * i + 1
            string[j] = func(string[j])

    string = "".join(string)

    return string


def return_regular(string, regular, function):
    string = re.split(regular, string)

    if string[0] == "":
        string = remove_elements(string, "")
        if len(string) == 1:
            N = 1
        else:
            N = int(len(string) / 2)
        for i in range(N):
            j = 2 * i
            # string[j] = "\\ul{" + string[j] + "}"
            string[j] = function(string[j])

    else:
        string = remove_elements(string, "")
        N = int(len(string) / 2)
        for i in range(N):
            j = 2 * i + 1
            string[j] = function(string[j])
            # string[j] = "\\ul{" + string[j] + "}"

    string = "".join(string)

    return string
