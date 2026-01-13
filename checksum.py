import re

# Defining constants
CHECKSUM_WEIGHTS = [9, 4, 5, 4, 3, 2]
CHECKSUM_KEY = list("AZYXUTSRPMLKJHGEDCB")
PLATE_RE = re.compile(r"([A-Z]{1,3})(\d{1,4})([A-Z]?)")


# function to compute checksum
# - returns checksum letter
def compute_checksum(prefix, numerals):

    # PREFIX - use last 2 letters, or 1 letter
    last2 = prefix[-2:]

    # PREFIX - convert letters to ascii to map to alphabet position
    # - add 0 to the front of single letter prefixes 
    if len(last2) == 1:
        p1, p2 = 0, ord(last2) - ord('A') + 1
    else:
        p1 = ord(last2[0]) - ord('A') + 1
        p2 = ord(last2[1]) - ord('A') + 1

    # NUMERAL - add 0s to the front of non 4-digit numerals
    digits = [int(c) for c in numerals.zfill(4)] 

    # combine prefix and numeral
    values = [p1, p2] + digits                    

    # compute total by multiplying values by weight and summing them
    total = sum(w * v for w, v in zip(CHECKSUM_WEIGHTS, values))

    # return checksum letter
    return CHECKSUM_KEY[total % 19]



# function to check if plate is valid
# - returns msg + boolean (True if valid/ False if invalid)
def plate_check(plate):

    # strip input of trailing spaces and uppercase it
    plate = plate.strip().upper()

    # check plate length
    if not (1 < len(plate) <= 8):
        return "Invalid vehicle plate!\n(Input length must be between 2 and 8 characters)", False

    m = PLATE_RE.fullmatch(plate)
    if not m:
        return "Invalid vehicle plate!\n(Format must be PREFIX + NUMERAL + CHECKSUM)", False

    prefix, numerals, given = m.groups()
    expected = compute_checksum(prefix, numerals)

    if given == "":
        return f"Missing checksum! Checksum expected: '{expected}'!", False

    if given != expected:
        return f"Invalid checksum! Checksum expected: '{expected}'!", False


    return "Valid vehicle plate!", True



if __name__ == "__main__":
    vehicle_plate: str = input("Enter plate: ")
    print(plate_check(vehicle_plate))
