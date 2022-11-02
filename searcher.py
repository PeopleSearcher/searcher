from google import make_request
from nalog import parse_nalog

fio = "Власов Александр Александрович"


nalog = parse_nalog(fio=fio)
internet = make_request("fio", fio)
print(nalog)
print(internet)