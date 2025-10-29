import fitz
import re

def _ints_from_column(title: str, text: str):
    # Find the title, then capture 9 numeric tokens that follow in the column
    m = re.search(rf'{re.escape(title)}[\s\S]+?((\d+\.?\d*\s+){{9}})', text)
    if not m:
        return []
    vals = []
    for tok in m.group(1).split():
        try:
            vals.append(int(float(tok)))
        except ValueError:
            pass
    return vals

def _mph_to_ms(x):  # mph to m/s rounded
    return str(round(float(x) * 0.44704))

def run(pdf_path: str) -> dict:
    with fitz.open(pdf_path) as doc:
        text = "".join(p.get_text() for p in doc)

    temps   = _ints_from_column("Temperature (F)", text)
    precip  = _ints_from_column("Precip Chance (%)", text)
    humid   = _ints_from_column("Relative Humidity (%)", text)
    wspd    = _ints_from_column("Wind Spd (mph)", text)
    wgst    = _ints_from_column("Wind Gust (mph)", text)

    out = {
        "HighF":   str(max(temps)) if temps else "N/A",
        "LowF":    str(min(temps)) if temps else "N/A",
        "RainPct": (str(max(precip)) + "%") if precip else "N/A",
        "HumPct":  (str(max(humid)) + "%") if humid else "N/A",
        "WindMS":  _mph_to_ms(max(wspd)) if wspd else "N/A",
        "GustMS":  _mph_to_ms(max(wgst)) if wgst else "N/A",
        "TStorm":  "<30%"
    }
    return out
