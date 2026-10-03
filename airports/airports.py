import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

AIRPORTS_SRC = Path("airports(vse).csv")
RUNWAYS_SRC = Path("runways.csv")
OUT_CSV = Path("airports.csv")
OUT_JSON = Path("airports.json")

FIELDS = [
    "ICAO", "Latitude", "Longitude", "Status", "Type",
    "Country", "Elevation", "Timezone", "Runways",
]

COUNTRY_NAMES = {
    "AD": "Andorra", "AE": "United Arab Emirates", "AF": "Afghanistan",
    "AG": "Antigua and Barbuda", "AI": "Anguilla", "AL": "Albania",
    "AM": "Armenia", "AO": "Angola", "AQ": "Antarctica", "AR": "Argentina",
    "AS": "American Samoa", "AT": "Austria", "AU": "Australia", "AW": "Aruba",
    "AZ": "Azerbaijan", "BA": "Bosnia and Herzegovina", "BB": "Barbados",
    "BD": "Bangladesh", "BE": "Belgium", "BF": "Burkina Faso",
    "BG": "Bulgaria", "BH": "Bahrain", "BI": "Burundi", "BJ": "Benin",
    "BL": "Saint Barthelemy", "BM": "Bermuda", "BN": "Brunei", "BO": "Bolivia",
    "BQ": "Bonaire", "BR": "Brazil", "BS": "Bahamas", "BT": "Bhutan",
    "BW": "Botswana", "BY": "Belarus", "BZ": "Belize", "CA": "Canada",
    "CC": "Cocos Islands", "CD": "Democratic Republic of the Congo",
    "CF": "Central African Republic", "CG": "Republic of the Congo",
    "CH": "Switzerland", "CI": "Cote d'Ivoire", "CK": "Cook Islands",
    "CL": "Chile", "CM": "Cameroon", "CN": "China", "CO": "Colombia",
    "CR": "Costa Rica", "CU": "Cuba", "CV": "Cabo Verde", "CW": "Curacao",
    "CX": "Christmas Island", "CY": "Cyprus", "CZ": "Czechia",
    "DE": "Germany", "DJ": "Djibouti", "DK": "Denmark", "DM": "Dominica",
    "DO": "Dominican Republic", "DZ": "Algeria", "EC": "Ecuador",
    "EE": "Estonia", "EG": "Egypt", "EH": "Western Sahara", "ER": "Eritrea",
    "ES": "Spain", "ET": "Ethiopia", "FI": "Finland", "FJ": "Fiji",
    "FK": "Falkland Islands", "FM": "Micronesia", "FO": "Faroe Islands",
    "FR": "France", "GA": "Gabon", "GB": "United Kingdom", "GD": "Grenada",
    "GE": "Georgia", "GF": "French Guiana", "GG": "Guernsey",
    "GH": "Ghana", "GI": "Gibraltar", "GL": "Greenland", "GM": "Gambia",
    "GN": "Guinea", "GP": "Guadeloupe", "GQ": "Equatorial Guinea",
    "GR": "Greece", "GS": "South Georgia", "GT": "Guatemala",
    "GU": "Guam", "GW": "Guinea-Bissau", "GY": "Guyana", "HK": "Hong Kong",
    "HM": "Heard and McDonald Islands", "HN": "Honduras", "HR": "Croatia",
    "HT": "Haiti", "HU": "Hungary", "ID": "Indonesia", "IE": "Ireland",
    "IL": "Israel", "IM": "Isle of Man", "IN": "India",
    "IO": "British Indian Ocean Territory", "IQ": "Iraq", "IR": "Iran",
    "IS": "Iceland", "IT": "Italy", "JE": "Jersey", "JM": "Jamaica",
    "JO": "Jordan", "JP": "Japan", "KE": "Kenya", "KG": "Kyrgyzstan",
    "KH": "Cambodia", "KI": "Kiribati", "KM": "Comoros",
    "KN": "Saint Kitts and Nevis", "KP": "North Korea", "KR": "South Korea",
    "KW": "Kuwait", "KY": "Cayman Islands", "KZ": "Kazakhstan",
    "LA": "Laos", "LB": "Lebanon", "LC": "Saint Lucia",
    "LI": "Liechtenstein", "LK": "Sri Lanka", "LR": "Liberia", "LS": "Lesotho",
    "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "LY": "Libya",
    "MA": "Morocco", "MC": "Monaco", "MD": "Moldova", "ME": "Montenegro",
    "MF": "Saint Martin", "MG": "Madagascar", "MH": "Marshall Islands",
    "MK": "North Macedonia", "ML": "Mali", "MM": "Myanmar", "MN": "Mongolia",
    "MO": "Macao", "MP": "Northern Mariana Islands", "MQ": "Martinique",
    "MR": "Mauritania", "MS": "Montserrat", "MT": "Malta", "MU": "Mauritius",
    "MV": "Maldives", "MW": "Malawi", "MX": "Mexico", "MY": "Malaysia",
    "MZ": "Mozambique", "NA": "Namibia", "NC": "New Caledonia", "NE": "Niger",
    "NF": "Norfolk Island", "NG": "Nigeria", "NI": "Nicaragua",
    "NL": "Netherlands", "NO": "Norway", "NP": "Nepal", "NR": "Nauru",
    "NU": "Niue", "NZ": "New Zealand", "OM": "Oman", "PA": "Panama",
    "PE": "Peru", "PF": "French Polynesia", "PG": "Papua New Guinea",
    "PH": "Philippines", "PK": "Pakistan", "PL": "Poland",
    "PM": "Saint Pierre and Miquelon", "PR": "Puerto Rico", "PS": "Palestine",
    "PT": "Portugal", "PW": "Palau", "PY": "Paraguay", "QA": "Qatar",
    "RE": "Reunion", "RO": "Romania", "RS": "Serbia", "RU": "Russian Federation",
    "RW": "Rwanda", "SA": "Saudi Arabia", "SB": "Solomon Islands",
    "SC": "Seychelles", "SD": "Sudan", "SE": "Sweden", "SG": "Singapore",
    "SH": "Saint Helena", "SI": "Slovenia", "SK": "Slovakia",
    "SL": "Sierra Leone", "SM": "San Marino", "SN": "Senegal", "SO": "Somalia",
    "SR": "Suriname", "SS": "South Sudan", "ST": "Sao Tome and Principe",
    "SV": "El Salvador", "SX": "Sint Maarten", "SY": "Syria", "SZ": "Eswatini",
    "TC": "Turks and Caicos Islands", "TD": "Chad",
    "TF": "French Southern Territories", "TG": "Togo", "TH": "Thailand",
    "TJ": "Tajikistan", "TL": "Timor-Leste", "TM": "Turkmenistan",
    "TN": "Tunisia", "TO": "Tonga", "TR": "Turkiye", "TT": "Trinidad and Tobago",
    "TV": "Tuvalu", "TW": "Taiwan", "TZ": "Tanzania", "UA": "Ukraine",
    "UG": "Uganda", "UM": "United States Minor Outlying Islands",
    "US": "United States", "UY": "Uruguay", "UZ": "Uzbekistan", "VA": "Holy See",
    "VC": "Saint Vincent and the Grenadines", "VE": "Venezuela",
    "VG": "British Virgin Islands", "VI": "United States Virgin Islands",
    "VN": "Vietnam", "VU": "Vanuatu", "WF": "Wallis and Futuna",
    "WS": "Samoa", "XK": "Kosovo", "YE": "Yemen", "YT": "Mayotte",
    "ZA": "South Africa", "ZM": "Zambia", "ZW": "Zimbabwe",
}

SURFACE_RULES = [
    (r"^\s*$|UNPAVED|UNPEVED|NOT PAVED|^N/?A|^NONE", "UNPAVED"),
    (r"PAVED|PAVEMENT|PAVE\b|SURFACE PAVED|^PAV", "PAVED"),
    (r"WATER|\bWAT\b|LAKE|SEA|OCEAN", "WATER"),
    (r"SNOW|ICE|FROZEN", "ICE"),
    (r"ASPH?|ASPHALT|ASP\b|ASFALT|ASPALT|ASHPALT|ASHPAULT", "ASPH"),
    (r"CONC|\bCON\b|CON/|CEMET", "CON"),
    (r"GRASS|\bGRAS\b|\bGRS\b|TURF|SOD|HERBA|LAWN|^GRA\b", "TURF"),
    (r"GRAVEL|GRVL|\bGVL\b|\bGRV\b|\bGRE\b|PI[CÇ]|LIME|SHINGLE|\bMAC\b", "GRVL"),
    (r"SAND|\bSAN\b", "SAND"),
    (r"DIRT|EARTH|SOIL|LOAM|\bCLAY\b|\bCLA\b|MUD|CALICHE|\bBROWN\b"
     r"|\bRED\b|\bBLACK\b|SILT|CORAL|GROUND", "DIRT"),
    (r"BITUM|\bBIT\b|\bTAR\b|MACADAM|TREAT|SEAL|CHIPSEAL|CRUSHED", "BIT"),
    (r"METAL|\bMET\b|STEEL|ALUM|ROOF|\bDECK\b|PIER", "METAL"),
    (r"PIERCED|PSP|PLANK|\bMATS?\b|MEMBRANE|NEOPRENE|\bPEM\b", "PSP"),
    (r"BRICK|COBBLE", "BRICK"),
    (r"WOOD|TIMBER", "WOOD"),
]

RUNWAY_RE = re.compile(r"^([^|]*)\|([^|]*)\|([^|]*)$")


def normalize_surface(raw: str) -> str:
    s = (raw or "").strip().upper().replace("&", "/")
    for pattern, code in SURFACE_RULES:
        if re.search(pattern, s):
            return code
    s = re.sub(r"\s+", " ", s).strip()
    if not s or len(s) <= 2:
        return "UNK"
    return "UNK" if "UNKNOWN" in s else s[:24]


def reciprocal(ident: str) -> str | None:
    m = re.match(r"^(\d{1,2})\s*([LRC]?)$", (ident or "").strip())
    if not m:
        return None
    n = int(m.group(1))
    if not 1 <= n <= 36:
        return None
    letter = {"L": "R", "R": "L", "C": "C"}.get(m.group(2), "")
    width = len(m.group(1))
    return f"{(n + 17) % 36 + 1:0{width}d}{letter}"


def runway_id(le_ident: str) -> str:
    le = (le_ident or "").strip()
    he = reciprocal(le)
    return f"{le}/{he}" if he else le


def to_number(raw: str):
    s = (raw or "").strip()
    if not s:
        return None
    try:
        return int(s) if re.fullmatch(r"-?\d+", s) else float(s)
    except ValueError:
        return None


class Timezones:
    def __init__(self):
        self.tf = TimezoneFinder()
        self.now = datetime.now(timezone.utc)
        self.cache: dict[tuple[int, int], int | None] = {}

    def offset(self, lat, lon):
        if lat is None or lon is None:
            return None
        key = (round(lat * 2), round(lon * 2))
        if key in self.cache:
            return self.cache[key]
        name = self.tf.timezone_at(lat=lat, lng=lon) or \
            self.tf.certain_timezone_at(lat=lat, lng=lon)
        value = None
        if name:
            delta = self.now.astimezone(ZoneInfo(name)).utcoffset()
            value = int(delta.total_seconds() // 3600)
        self.cache[key] = value
        return value


def load_runways() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    with open(RUNWAYS_SRC, encoding="utf-8", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            grouped.setdefault((r.get("airport_ref") or "").strip(), []).append({
                "ID": runway_id(r.get("le_ident") or ""),
                "Length": to_number(r.get("length_ft") or ""),
                "Surface": normalize_surface(r.get("surface") or ""),
            })
    return grouped


def build() -> list[dict]:
    runways_by_ref = load_runways()
    tz = Timezones()

    with open(AIRPORTS_SRC, encoding="utf-8", errors="replace", newline="") as f:
        airports = list(csv.DictReader(f))

    result = []
    for a in airports:
        lat = to_number(a.get("latitude_deg") or "")
        lon = to_number(a.get("longitude_deg") or "")
        country = (a.get("iso_country") or "").strip()
        result.append({
            "ICAO": (a.get("gps_code") or a.get("ident") or "").strip(),
            "Latitude": lat,
            "Longitude": lon,
            "Status": "close" if (a.get("type") or "") == "closed" else "open",
            "Type": (a.get("type") or "").strip(),
            "Country": COUNTRY_NAMES.get(country, country),
            "Elevation": to_number(a.get("elevation_ft") or ""),
            "Timezone": tz.offset(lat, lon),
            "Runways": runways_by_ref.get((a.get("id") or "").strip(), []),
        })
    return result


def write_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for r in rows:
            row = dict(r)
            row["Runways"] = "; ".join(
                f"{rw['ID']}|{rw['Length'] if rw['Length'] is not None else ''}"
                f"|{rw['Surface']}"
                for rw in r["Runways"]
            )
            writer.writerow(row)


def write_json(rows: list[dict], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)


def main() -> None:
    rows = build()
    write_csv(rows, OUT_CSV)
    write_json(rows, OUT_JSON)

    with_tz = sum(1 for r in rows if r["Timezone"] is not None)
    with_rw = sum(1 for r in rows if r["Runways"])
    closed = sum(1 for r in rows if r["Status"] == "close")
    print(f"airports      : {len(rows)}")
    print(f"timezone found: {with_tz} ({with_tz / len(rows) * 100:.1f}%)")
    print(f"with runways  : {with_rw} ({with_rw / len(rows) * 100:.1f}%)")
    print(f"closed        : {closed}")
    print(f"-> {OUT_CSV}, {OUT_JSON}")


if __name__ == "__main__":
    main()
