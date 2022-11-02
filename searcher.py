from google import make_request
from nalog import parse_nalog

fio = "Власов Александр Александрович"

nalog = parse_nalog(fio=fio)
internet = make_request("fio", fio)  # only with vpn or proxy otherwise hide this line

print(nalog)
print(internet)
