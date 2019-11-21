import re


assert re.sub(r"(a|b)", r"-\1-", "aecbrdr") == "-a-ec-b-rdr"

assert re.sub(r"(a|b)", r"-\g<1>-", "aecbrdr") == "-a-ec-b-rdr"
