#!/usr/bin/env python3
import argparse
import datetime
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEED = 20261106

PAGE_WIDTH, PAGE_HEIGHT = 595.32, 841.92
SIZE = 9.0
LEADING = 13.0
LEFT, MIDDLE, RIGHT = 36.0, 300.0, 440.0
TITLE = "HAEMODIALYSIS CENTRE ORDER FORM"
MARK = "SYNTHETIC SAMPLE"
NOTE = "Synthetic sample, not a real order."

WOMEN = ("ARYA STARK|SANSA STARK|CATELYN STARK|LYANNA STARK|TALISA STARK|CERSEI LANNISTER|DAENERYS TARGARYEN|RHAENYS TARGARYEN|"
         "MARGAERY TYRELL|OLENNA TYRELL|BRIENNE TARTH|YARA GREYJOY|LYANNA MORMONT|MAEGE MORMONT|ELLARIA SAND|OBARA SAND|"
         "NYMERIA SAND|TYENE SAND|SHIREEN BARATHEON|SELYSE BARATHEON|MYRCELLA BARATHEON|LYSA ARRYN|MEERA REED|ROSLIN FREY").split("|")
MEN = ("JON SNOW|EDDARD STARK|ROBB STARK|BRAN STARK|RICKON STARK|BENJEN STARK|TYRION LANNISTER|JAIME LANNISTER|TYWIN LANNISTER|"
       "KEVAN LANNISTER|LANCEL LANNISTER|ROBERT BARATHEON|STANNIS BARATHEON|RENLY BARATHEON|JOFFREY BARATHEON|TOMMEN BARATHEON|"
       "GENDRY WATERS|THEON GREYJOY|BALON GREYJOY|EURON GREYJOY|JORAH MORMONT|JEOR MORMONT|SAMWELL TARLY|RANDYLL TARLY|"
       "DAVOS SEAWORTH|SANDOR CLEGANE|GREGOR CLEGANE|PETYR BAELISH|OBERYN MARTELL|DORAN MARTELL|LORAS TYRELL|MACE TYRELL|"
       "ROOSE BOLTON|RAMSAY BOLTON|WALDER FREY|EDMURE TULLY|ROBIN ARRYN|BERIC DONDARRION|PODRICK PAYNE|BARRISTAN SELMY|"
       "DAARIO NAHARIS|JOJEN REED|ALLISER THORNE|TORMUND GIANTSBANE|VISERYS TARGARYEN|AEMON TARGARYEN").split("|")
DOCTORS = ["Doctor " + w for w in "Amber Birch Cedar Dune Ember Flint Grove Heath".split()]
CONSULTANTS = ["Consultant " + w for w in "Indigo Juniper Kestrel Linden Maple Nectar".split()]
STREETS = ["EXAMPLE ROAD", "SAMPLE AVENUE", "PLACEHOLDER CRESCENT", "FICTION DRIVE", "MOCKUP LANE"]
SERVICES = ["General Medicine"] * 5 + ["Renal Medicine", "Cardiology", "General Surgery", "Orthopaedic Surgery", "Neurology"]
CENTRES = ["NKF DIALYSIS CENTRE", "KDF DIALYSIS CENTRE", "FRESENIUS KIDNEY CARE", "DIAVERUM RENAL CARE",
           "RENAL LIFE CENTRE", "HOPE DIALYSIS CENTRE", "IMMANUEL DIALYSIS CENTRE"]
NO_CENTRE = ["New to dialysis this admission", "Acute kidney injury", "tba, tba", "00, 00"]
ALLERGIES = ["Penicillin", "Sulfonamides", "Iodinated contrast", "Latex", "Aspirin"]
PRIORITY = {1: "Emergency", 2: "Urgent", 3: "Routine"}
SITES = {
    "AVF": ["Radio-Cephalic", "Brachio-Cephalic", "Brachio-Basilic"],
    "AVG": ["Forearm Loop", "Upper Arm"],
    "Tunnelled Vascular Catheter": ["Right Internal Jugular Vein", "Left Internal Jugular Vein"],
    "Non-Tunnelled Vascular Catheter": ["Right Internal Jugular Vein", "Right Femoral Vein", "Left Femoral Vein"],
}
REMARKS_EARLIER = ["aim for AM slot", "AM slot if possible", "early slot please, scan later today"]
REMARKS_LATER = ["await TDC insertion", "pending TDC insertion this morning", "awaiting angioplasty"]
REMARKS_PLAIN = ["UF as tolerated", "for discharge after dialysis", "please take post-dialysis bloods", "review dry weight",
                 "blood pressure borderline, go gently", "transfer back to ward after dialysis", "dressing change at line site",
                 "check access flow before starting", "hold heparin, recent biopsy", "family will accompany"]
SCANS = [("CT Abdomen", "Routine"), ("Ultrasound Kidneys", "Routine"), ("Echocardiogram", "Routine"),
         ("Tunnelled Line Insertion", "Routine"), ("Fistulogram", "Urgent")]


def weighted(rng, pairs):
    return rng.choices([p[0] for p in pairs], [p[1] for p in pairs])[0]


def long_date(day):
    return day.strftime("%d %b %Y")


class Patient:

    def __init__(self, rng, number, name, sex):
        self.name = name
        self.ic = "X%07d%s" % (rng.randrange(10 ** 7), rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        self.number = number
        self.born = datetime.date(rng.randint(1938, 1990), rng.randint(1, 12), rng.randint(1, 28))
        self.sex = sex
        self.address = "Blk/Hse:%d,Level/Unit:%02d-%02d %s %d . Singapore 000%03d" % (
            rng.randint(1, 999), rng.randint(1, 30), rng.randint(1, 99), rng.choice(STREETS), rng.randint(1, 30), rng.randint(1, 999))
        self.account = "SAMPLE%05d" % number
        self.ward_class = rng.choice(["CLASS A", "CLASS B1", "CLASS B2", "CLASS C", "CLASS C"])
        self.service = rng.choice(SERVICES)
        ward, room, bed = rng.randint(1, 20), rng.randint(1, 40), rng.randint(1, 8)
        self.location = weighted(rng, [("DEMO-W%02d-%04d-%02d" % (ward, room, bed), 86),
                                       ("DEMO-W%02d-HDU-%04d-%02d" % (ward, room, bed), 10), ("DEMO HOLDING AREA", 4)])
        self.allergy = weighted(rng, [("(None)", 75), (rng.choice(ALLERGIES), 25)])
        self.hp = weighted(rng, [("(None)", 66), ("MRSA", 16), ("VRE", 5), ("CP-CRE", 4), ("C. difficile", 3),
                                 ("MRSA,VRE", 3), ("ESBL", 3)])
        self.hep_b = weighted(rng, [("No", 86), ("Pending Test Result", 8), ("Yes", 6)])
        self.access = weighted(rng, [("AVF", 45), ("Tunnelled Vascular Catheter", 38), ("AVG", 5), ("Non-Tunnelled Vascular Catheter", 12)])
        self.side = rng.choice(["Left", "Right"])
        self.site = rng.choice(SITES[self.access])
        self.dry_weight = rng.randint(84, 196) / 2
        self.centre = None
        if rng.random() < 0.72:
            self.centre = "%s (SAMPLE BRANCH) |Blk 999 Example Road %d #01-99 S(000%03d) |T:0000 %04d |F:0000 %04d" % (
                rng.choice(CENTRES), rng.randint(1, 30), rng.randint(1, 999), number, number + 5000)
        else:
            self.no_centre = rng.choice(NO_CENTRE)
        self.days = rng.choice(["Monday; Wednesday; Friday", "Tuesday; Thursday; Saturday"])


def clinical(rng, patient, day, priority, remarks, scans, access_ok=True, order_number=0):
    treatment = weighted(rng, [("Intermittent HD", 80), ("SLED", 10), ("HDF", 6), ("Sequential", 4)])
    length = "%02d:00" % rng.choice([6, 8]) if treatment == "SLED" else rng.choice(["03:00", "03:30", "04:00", "04:00", "04:30"])
    ordered = day - datetime.timedelta(days=rng.choice([0, 1, 1, 2]))
    ordered_at = "%s %02d:%02d:%02d" % (long_date(ordered), rng.randint(7, 19), rng.randint(0, 59), rng.randint(0, 59))
    first = day - datetime.timedelta(days=rng.randint(1, 40))
    tested = day - datetime.timedelta(days=rng.randint(2, 90))
    hbsag = {"No": "Non-Reactive, " + long_date(tested), "Yes": "Reactive, " + long_date(tested),
             "Pending Test Result": "Not Traced/Not Done"}[patient.hep_b]
    heparin = rng.random() < 0.45
    catheter = "Catheter" in patient.access
    flow_b, flow_d = rng.choice([200, 220, 250, 280, 300, 320, 350]), rng.choice([300, 400, 500, 600, 800])

    def line(*runs):
        return list(runs)

    lines = [
        line((LEFT, "NAME: " + patient.name, False), (MIDDLE, "NRIC: " + patient.ic, False)),
        line((LEFT, "BIRTH DATE: " + long_date(patient.born), False), (MIDDLE, "SEX: " + patient.sex, False), (RIGHT, "RACE: Not stated", False)),
        line((LEFT, "ADDRESS: " + patient.address, False)),
        line((LEFT, "ACCOUNT: " + patient.account, False), (MIDDLE, "CLASS: " + patient.ward_class, False)),
        line((LEFT, "SERVICE: " + patient.service, False)),
        line((LEFT, "LOCATION: " + patient.location, False)),
        line((LEFT, "Requesting Doctor: " + rng.choice(DOCTORS), False), (MIDDLE, "Order Date: " + ordered_at, False)),
        line((LEFT, "Consultant-in-charge: " + rng.choice(CONSULTANTS), False)),
    ]
    order_box = [(LEFT, "Order ID: SMP%06d" % order_number, False), (MIDDLE - 90, "REQUESTED DATE: " + long_date(day), False)]
    if rng.random() < 0.85:
        order_box.append((MIDDLE + 90, "1st Dialysis (this admission) : " + long_date(first), False))
    lines += [order_box, line((LEFT, "Haemodialysis (%s)" % treatment, True))]

    lines.append(line((LEFT, "PRESCRIPTION FROM OUTPATIENT DIALYSIS CENTRE", True)))
    if patient.centre:
        lines += [line((LEFT, "Usual Dialysis Centre : " + patient.centre, False)),
                  line((LEFT, "Dialysis Type : Intermittent HD", False), (MIDDLE - 90, "Dialysis Days : " + patient.days, False), (RIGHT, "Session Time (hrs) : 04:00", False)),
                  line((LEFT, "Dry Weight (kg) : %g" % patient.dry_weight, False), (MIDDLE - 90, "QB (ml/min) : %d" % flow_b, False),
                       (MIDDLE + 40, "QD (ml/min) : %d" % flow_d, False), (RIGHT, "AntiCoag : nil", False))]
    else:
        lines += [line((LEFT, "Usual Dialysis Centre : " + patient.no_centre, False)),
                  line((LEFT, "Dialysis Type :", False), (MIDDLE - 90, "Dialysis Days :", False), (RIGHT, "Session Time (hrs) :", False)),
                  line((LEFT, "Dry Weight (kg) :", False), (MIDDLE - 90, "QB (ml/min) :", False), (MIDDLE + 40, "QD (ml/min) :", False), (RIGHT, "AntiCoag :", False))]
    lines += [
        line((LEFT, "Allergy (If any) : " + patient.allergy, False)),
        line((LEFT, "Priority : %d %s" % (priority, PRIORITY[priority]), False)),
        line((LEFT, "Schedule : " + weighted(rng, [("3 times per week", 80), ("2 times per week", 12), ("Daily", 8)]), False)),
        line((LEFT, "Length (hrs) : " + length, False), (MIDDLE, "Mode of Transport : " + weighted(rng, [("Wheel Chair", 55), ("Portable", 20), ("Bed", 25)]), False)),
        line((LEFT, "ACCESS", True)),
        line((LEFT, "Functioning Vascular Access present? : " + ("Yes" if access_ok else "No"), False), (MIDDLE, "Access Side : " + patient.side, False)),
        line((LEFT, "Type of Vascular Access to be used : " + patient.access + (", Buttonhole :" + ("Yes" if rng.random() < 0.08 else "No") if patient.access == "AVF" else ""), False),
             (MIDDLE, "Access Site : " + patient.site, False)),
        line((LEFT, "Transonic Flow : " + ("Yes" if rng.random() < 0.1 else "No"), False), (MIDDLE, "Filter: " + weighted(rng, [("High Flux", 90), ("Low Flux", 10)]), False)),
    ]
    if catheter:
        changed = day - datetime.timedelta(days=rng.randint(1, 6))
        lines.append(line((LEFT, "Tego Needleless Connector - Date of Change : " + long_date(changed), False),
                          (MIDDLE, "Tego Needleless Connector -Due : " + long_date(changed + datetime.timedelta(days=7)), False)))
    lines.append(line((LEFT, "ANTI-COAG", True), (MIDDLE, "FLUID MANAGEMENT", True)))
    lines.append(line((LEFT, "Allergic to Heparin? : " + ("No" if heparin or rng.random() < 0.9 else "Yes"), False),
                      (MIDDLE, "Ultrafiltration (L) : %g" % (rng.randint(1, 8) / 2), False)))
    lines.append(line((LEFT, "Heparin : " + ("Yes" if heparin else "No"), False), (MIDDLE, "Dry Weight (kg) : %g" % patient.dry_weight, False)))
    if heparin:
        lines.append(line((LEFT, "Heparin Initial (Units) : %d" % rng.choice([500, 1000, 1500, 2000]), False),
                          (MIDDLE, "Heparin hourly (Units) : %d" % rng.choice([200, 300, 500, 800]), False)))
    lines += [
        line((LEFT, "VIROLOGY RESULTS", True), (MIDDLE, "VIROLOGY STATUS", True)),
        line((LEFT, "HIV : Non-Reactive, " + long_date(tested), False), (MIDDLE, "HIV Case : No", False)),
        line((LEFT, "HepBsAg : " + hbsag, False), (MIDDLE, "HepB Case : " + patient.hep_b, False)),
        line((LEFT, "Anti-HCV : Non-Reactive, " + long_date(tested), False), (MIDDLE, "HepC Case : No", False)),
        line((MIDDLE, "HP (If any) : " + patient.hp, False)),
        line((LEFT, "DIALYSATE", True)),
        line((LEFT, "QB (ml/min) : %d" % flow_b, False),
             (MIDDLE - 130, "Type of Dialysate : Glucose, Cal %s, K %s" % (rng.choice(["1.25", "1.5", "1.75"]), rng.choice(["1.5", "2.0", "3.0"])), False),
             (RIGHT - 20, "Fixed NA+ conc (mmol/L) : %d" % rng.choice([135, 138, 140]), False)),
        line((LEFT, "QD (ml/min) : %d" % flow_d, False), (RIGHT - 20, "Dialysate Temperature : %s" % rng.choice(["35.5", "36", "36.5"]), False)),
    ]
    if remarks:
        lines.append(line((LEFT, "Additional Remarks / Instructions: " + remarks[0], False)))
        lines += [line((LEFT + 150, more, False)) for more in remarks[1:]]
    lines += [line((LEFT, "Special Notes: " + NOTE, False)), line((LEFT, "DIABETIC :", False))]
    return lines, [line((LEFT, "Scheduled Radiology Orders", True))] + [
        line((LEFT, "%s %s" % (when.strftime("%d/%m/%Y"), when.strftime("%H:%M")), False), (LEFT + 80, name, False), (RIGHT, urgency, False))
        for when, name, urgency in scans]


def escape(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def page_content(lines, marked):
    out, y = [], PAGE_HEIGHT - 42
    if marked:
        out.append("BT /F2 9 Tf 1 0 0 1 %.2f %.2f Tm (%s) Tj ET" % (LEFT, y, MARK))
        y -= LEADING + 4
        out.append("BT /F2 13 Tf 1 0 0 1 %.2f %.2f Tm (%s) Tj ET" % (LEFT, y, TITLE))
        y -= LEADING + 8
    for runs in lines:
        for x, text, bold in runs:
            out.append("BT /%s %g Tf 1 0 0 1 %.2f %.2f Tm (%s) Tj ET" % ("F2" if bold else "F1", SIZE, x, y, escape(text)))
        if runs[0][2]:
            out.append("0.4 w %.2f %.2f m %.2f %.2f l S" % (LEFT, y - 3, PAGE_WIDTH - LEFT, y - 3))
            y -= 4
        y -= LEADING
    return "\n".join(out) + "\n"


def pdf_file(contents, title):
    n = len(contents)
    font = "<< /Type /Font /Subtype /Type1 /BaseFont /%s /Encoding /WinAnsiEncoding >>"
    objects = ["<< /Type /Catalog /Pages 2 0 R >>",
               "<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join("%d 0 R" % (6 + 2 * i) for i in range(n)), n),
               font % "Times-Roman", font % "Times-Bold",
               "<< /Title (%s) /Producer (citrix-dialysis-allocator sample generator) >>" % title]
    for i, content in enumerate(contents):
        objects.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %g %g] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents %d 0 R >>"
                       % (PAGE_WIDTH, PAGE_HEIGHT, 7 + 2 * i))
        objects.append("<< /Length %d >>\nstream\n%sendstream" % (len(content), content))
    data, offsets = "%PDF-1.4\n", []
    for i, body in enumerate(objects):
        offsets.append(len(data))
        data += "%d 0 obj\n%s\nendobj\n" % (i + 1, body)
    table = len(data)
    data += "xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    data += "".join("%010d 00000 n \n" % off for off in offsets)
    data += "trailer\n<< /Size %d /Root 1 0 R /Info 5 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, table)
    return data.encode("ascii")


class Writer:

    def __init__(self, rng):
        self.rng, self.orders, self.files, self.pdf = rng, 0, 0, {}

    def order(self, patient, day, priority, remarks, scans, access_ok=True):
        self.orders += 1
        return clinical(self.rng, patient, day, priority, remarks, scans, access_ok, self.orders)

    def write(self, sheets):
        self.files += 1
        name = "order-%03d" % self.files
        total = len(sheets)
        contents = []
        for number, (lines, marked) in enumerate(sheets, 1):
            lines = lines + [[(LEFT, "Page %d of %d" % (number, total), False)]]
            contents.append(page_content(lines, marked))
        self.pdf[name] = pdf_file(contents, "Synthetic sample " + name)


def remarks_for(rng):
    pool = [REMARKS_EARLIER, REMARKS_LATER, REMARKS_PLAIN, REMARKS_PLAIN]
    wanted = weighted(rng, [(0, 40), (1, 45), (2, 15)])
    picked = rng.sample(pool[:3], wanted)
    return [rng.choice(group) for group in picked]


def scans_for(rng, day):
    if rng.random() > 0.18:
        return []
    name, urgency = rng.choice(SCANS)
    moment = datetime.datetime(day.year, day.month, day.day, rng.choice([9, 11, 14, 16]), rng.choice([0, 30]))
    return [(moment + datetime.timedelta(days=rng.choice([-1, 0, 0, 1])), name, urgency)]


def build(seed, today):
    rng = random.Random(seed)
    names = [(name, "Female") for name in WOMEN] + [(name, "Male") for name in MEN]
    rng.shuffle(names)
    writer = Writer(rng)
    next_patient = iter(range(1, len(names) + 1))

    def patient():
        number = next(next_patient)
        name, sex = names[number - 1]
        return Patient(rng, number, name, sex)

    def day_of(offset):
        return today + datetime.timedelta(days=offset)

    def one(someone, offset, priority=None, access_ok=True):
        priority = priority or weighted(rng, [(3, 78), (2, 12), (1, 10)])
        return writer.order(someone, day_of(offset), priority, remarks_for(rng), scans_for(rng, day_of(offset)), access_ok)

    for _ in range(46):
        lines, radiology = one(patient(), weighted(rng, [(0, 58), (1, 12), (2, 6), (-1, 16), (-2, 8)]))
        writer.write([(lines + radiology, True)])
    for _ in range(2):
        someone = patient()
        for offset in (-2, -1):
            lines, radiology = one(someone, offset, 3)
            writer.write([(lines + radiology, True)])
    for _ in range(3):
        lines, radiology = one(patient(), 0, 2, access_ok=False)
        writer.write([(lines + radiology, True)])
    someone = patient()
    for offset in (0, 2, 4):
        lines, radiology = one(someone, offset, 3)
        writer.write([(lines + radiology, True)])
    someone = patient()
    first, radiology_1 = one(someone, 1, 3)
    second, radiology_2 = one(someone, 3, 3)
    writer.write([(first + radiology_1, True), (second + radiology_2, True)])
    someone = patient()
    someone.hp = "(None)"
    lines, _ = one(someone, 0, 3)
    extra = writer.rng.choice(SCANS)
    moment = datetime.datetime(today.year, today.month, today.day, 15, 0)
    writer.write([(lines, True), ([[(LEFT, "Scheduled Radiology Orders", True)],
                                   [(LEFT, moment.strftime("%d/%m/%Y %H:%M"), False), (LEFT + 80, extra[0], False), (RIGHT, extra[1], False)]], False)])
    return writer


def main():
    parser = argparse.ArgumentParser(description="Make the synthetic orders in sample-orders/.")
    parser.add_argument("--today", type=datetime.date.fromisoformat, default=datetime.date.today(), help="the day the dates sit around")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    orders = ROOT / "sample-orders"
    orders.mkdir(parents=True, exist_ok=True)
    for old in orders.glob("order-*.pdf"):
        old.unlink()
    writer = build(args.seed, args.today)
    for name, data in writer.pdf.items():
        (orders / (name + ".pdf")).write_bytes(data)
    print("%d files holding %d orders, dates around %s" % (writer.files, writer.orders, args.today))


if __name__ == "__main__":
    main()
