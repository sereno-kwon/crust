#!/usr/bin/env python3
"""index.src.html → index.html

지오메트리 표 자리({{GEO_*}})를 아래 GEO 데이터로 채웁니다.
  python3 build.py            index.html 생성
  python3 build.py --preview  preview.html 생성 (이미지를 크러스트 CDN 원본 주소로 연결, 이미지 받기 전 확인용)
수치 출처: crustbikes.com 각 제품 페이지 지오메트리 차트 (단위 mm, 각도 °)
"""
import re, sys, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (행 이름, [사이즈별 값])
GEO = {
    "EVASION": {
        "sizes": [("Step-Thru", ""), ("S", "52"), ("M", "54"), ("XM", "56"), ("L", "58"), ("XL", "60")],
        "rows": [
            ("스택", [537, 537, 553, 576, 599, 628]),
            ("리치", [367, 367, 377, 382, 395, 406]),
            ("탑튜브 길이 (가상)", [520, 520, 540, 560, 580, 600]),
            ("탑튜브 길이 (C-C)", [507, 502, 524, 544, 567, 591]),
            ("탑튜브 슬로프 (°)", [24, 11, 8, 6, 5, 3]),
            ("싯튜브 길이 (C-T)", [466, 466, 499, 540, 573, 625]),
            ("헤드 앵글", [69.5, 69.5, 70, 71, 71, 71]),
            ("싯튜브 앵글", [74.5, 74.5, 74, 73, 73, 73]),
            ("헤드튜브 길이", [117, 117, 132, 153, 176, 208]),
            ("체인스테이 길이", [431] * 6),
            ("BB 높이", [292] * 6),
            ("BB 드롭", [64] * 6),
            ("스탠드오버", [695, 750, 777, 806, 835, 873]),
            ("포크 레이크", [45] * 6),
            ("트레일", [85] * 6),
            ("휠베이스", [1018, 1018, 1030, 1032, 1053, 1074]),
            ("프론트 센터", [595, 595, 604, 609, 630, 651]),
        ],
    },
    "TRAIL": {
        "sizes": [("S", "59"), ("M", "62"), ("L", "65")],
        "rows": [
            ("스택", [542, 575, 622]),
            ("리치", [430, 443, 458]),
            ("탑튜브 길이 (가상)", [590, 620, 640]),
            ("탑튜브 길이 (C-C)", [570, 593, 624]),
            ("탑튜브 슬로프 (°)", [22, 17, 13]),
            ("싯튜브 길이 (C-T)", [447, 525, 605]),
            ("헤드 앵글", [70, 71, 71]),
            ("싯튜브 앵글", [74, 73, 73]),
            ("헤드튜브 길이", [125, 155, 205]),
            ("체인스테이 길이", [431] * 3),
            ("BB 높이", [300] * 3),
            ("BB 드롭", [55] * 3),
            ("스탠드오버", [675, 723, 796]),
            ("포크 레이크", [45] * 3),
            ("트레일", [82, 75, 75]),
        ],
    },
    "BOMBORA": {
        "sizes": [("XS", "52"), ("S", "54"), ("M", "56"), ("L", "58"), ("XL", "60"), ("XXL", "62")],
        "rows": [
            ("스택", [540, 553, 576, 599, 628, 660]),
            ("리치", [365, 378, 382, 395, 406, 416]),
            ("탑튜브 길이 (가상)", [520, 540, 560, 580, 600, 620]),
            ("탑튜브 길이 (C-C)", [502, 525, 546, 569, 594, 619]),
            ("탑튜브 슬로프 (°)", [18.7, 14.1, 9.5, 6.1, 3.5, 1.2]),
            ("싯튜브 길이 (C-T)", [456, 502, 543, 574, 629, 670]),
            ("싯튜브 길이 (C-C)", [408, 455, 494, 529, 581, 622]),
            ("헤드 앵글", [69.5, 70, 71, 71, 71, 71]),
            ("싯튜브 앵글", [74.5, 74, 73, 73, 73, 73]),
            ("헤드튜브 길이", [121, 132, 153, 177, 208, 241]),
            ("체인스테이 길이", [425] * 6),
            ("BB 높이", [290] * 6),
            ("BB 드롭", [64] * 6),
            ("스탠드오버", [747, 775, 804, 832, 872, 907]),
            ("포크 레이크", [48] * 6),
            ("트레일", [81, 78, 71, 71, 71, 71]),
            ("휠베이스", [1008, 1020, 1023, 1043, 1064, 1085]),
        ],
    },
}


def num(v):
    return str(int(v)) if float(v).is_integer() else str(v)


def table(g):
    head = "".join(f"<th>{s}{f'<small>{c}</small>' if c else ''}</th>" for s, c in g["sizes"])
    body = "".join(
        f"<tr><th>{html.escape(name)}</th>" + "".join(f"<td>{num(v)}</td>" for v in vals) + "</tr>"
        for name, vals in g["rows"]
    )
    for name, vals in g["rows"]:
        assert len(vals) == len(g["sizes"]), name
    return f'<table class="geo"><thead><tr><th></th>{head}</tr></thead><tbody>{body}</tbody></table>'


def main():
    src = (ROOT / "index.src.html").read_text(encoding="utf-8")
    out = re.sub(r"\{\{GEO_(\w+)\}\}", lambda m: table(GEO[m.group(1)]), src)
    assert "{{" not in out, "채워지지 않은 자리표시자가 있습니다"

    if "--preview" in sys.argv:
        # images/... → 매니페스트의 원본 주소
        cdn = {}
        for line in (ROOT / ".github/image-manifest.txt").read_text().splitlines():
            if line.strip():
                url, dest = line.split()
                cdn[dest] = url
        out = re.sub(r"images/[\w/.-]+\.(?:jpg|png)", lambda m: cdn.get(m.group(0), m.group(0)), out)
        missing = sorted(set(re.findall(r'(?<![/\w])images/[\w/.-]+\.(?:jpg|png)', out)))
        if missing:
            print("매니페스트에 없는 이미지:", missing)
        (ROOT / "preview.html").write_text(out, encoding="utf-8")
        print("preview.html")
    else:
        # 페이지에서 쓰는 이미지가 모두 매니페스트에 있는지 확인
        listed = {l.split()[1] for l in (ROOT / ".github/image-manifest.txt").read_text().splitlines() if l.strip()}
        used = set(re.findall(r"images/[\w/.-]+\.(?:jpg|png)", out))
        for u in sorted(used - listed):
            print("매니페스트에 없는 이미지:", u)
        (ROOT / "index.html").write_text(out, encoding="utf-8")
        print("index.html")


if __name__ == "__main__":
    main()
