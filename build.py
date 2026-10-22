#!/usr/bin/env python3
"""index.src.html → index.html

지오메트리 표 자리({{GEO_*}})를 아래 GEO 데이터로 채웁니다.
  python3 build.py            index.html, en/index.html, ja/index.html 생성
  python3 build.py --preview  preview*.html 생성 (이미지를 크러스트 CDN 원본 주소로 연결)
번역: i18n/en.json, i18n/ja.json 의 strings는 "한국어 원문": "번역" 쌍입니다.
한국어 원문을 고치면 같은 키를 두 파일에서도 함께 고쳐야 합니다. 빌드 때 번역이 빠진 한국어가 있으면 목록을 출력합니다.
수치 출처: crustbikes.com 각 제품 페이지 지오메트리 차트 (단위 mm, 각도 °)
"""
import re, sys, html, json
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


GEO_LABELS = {
    "en": {"스택": "Stack", "리치": "Reach", "탑튜브 길이 (가상)": "Top tube (effective)", "탑튜브 길이 (C-C)": "Top tube (C-C)",
           "탑튜브 슬로프 (°)": "Top tube slope (°)", "싯튜브 길이 (C-T)": "Seat tube (C-T)", "싯튜브 길이 (C-C)": "Seat tube (C-C)",
           "헤드 앵글": "Head angle", "싯튜브 앵글": "Seat angle", "헤드튜브 길이": "Head tube", "체인스테이 길이": "Chainstay",
           "BB 높이": "BB height", "BB 드롭": "BB drop", "스탠드오버": "Standover", "포크 레이크": "Fork rake", "트레일": "Trail",
           "휠베이스": "Wheelbase", "프론트 센터": "Front center"},
    "ja": {"스택": "スタック", "리치": "リーチ", "탑튜브 길이 (가상)": "トップチューブ長（水平換算）", "탑튜브 길이 (C-C)": "トップチューブ長（C-C）",
           "탑튜브 슬로프 (°)": "トップチューブ傾斜（°）", "싯튜브 길이 (C-T)": "シートチューブ長（C-T）", "싯튜브 길이 (C-C)": "シートチューブ長（C-C）",
           "헤드 앵글": "ヘッド角", "싯튜브 앵글": "シート角", "헤드튜브 길이": "ヘッドチューブ長", "체인스테이 길이": "チェーンステー長",
           "BB 높이": "BBハイト", "BB 드롭": "BBドロップ", "스탠드오버": "スタンドオーバー", "포크 레이크": "フォークオフセット", "트레일": "トレイル",
           "휠베이스": "ホイールベース", "프론트 센터": "フロントセンター"},
}

SITE = "https://crustbikes.co.kr/"
LANGS = [("ko", "KO", ""), ("en", "EN", "en/"), ("ja", "JA", "ja/")]
HANGUL = re.compile("[가-힣]")


def lang_switch(cur):
    depth = "" if cur == "ko" else "../"
    return "".join(
        f'<a href="{depth}{path or "./"}" hreflang="{code}" lang="{code}"{" class=\"on\" aria-current=\"true\"" if code == cur else ""}>{label}</a>'
        for code, label, path in LANGS
    ).replace('href=".././"', 'href="../"')


HREFLANG = "\n".join(
    [f'<link rel="alternate" hreflang="{c}" href="{SITE}{p}">' for c, _, p in LANGS]
    + [f'<link rel="alternate" hreflang="x-default" href="{SITE}">']
)


def translate(html_text, tr):
    out = html_text
    for key in sorted(tr["strings"], key=len, reverse=True):
        val = tr["strings"][key]
        k = re.escape(key)
        out = re.sub(r"(>\s*)" + k + r"(\s*<)", lambda m: m.group(1) + val + m.group(2), out)
        out = out.replace(f'"{key}"', f'"{val}"')
    for pat, rep in tr["patterns"]:
        out = re.sub(pat, rep, out)
    return out


def dealers_json():
    """dealers.json → 페이지에 넣을 JSON. 좌표·필수 항목을 확인합니다."""
    data = json.loads((ROOT / "dealers.json").read_text(encoding="utf-8"))
    for d in data["dealers"]:
        for k in ("id", "type", "name", "region", "address", "lat", "lng"):
            assert k in d, f"dealers.json: {d.get('id', d.get('name'))} 에 {k} 항목이 없습니다"
        assert d["region"] in data["regions"], f"dealers.json: {d['id']} 의 region '{d['region']}' 이 regions에 없습니다"
        assert 33 < d["lat"] < 39 and 124 < d["lng"] < 132, f"dealers.json: {d['id']} 좌표가 한국 밖입니다"
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def finish(out):
    return out.replace("{{DEALERS}}", dealers_json())


def render(code):
    src = (ROOT / "index.src.html").read_text(encoding="utf-8")
    out = re.sub(r"\{\{GEO_(\w+)\}\}", lambda m: table(GEO[m.group(1)]), src)
    out = out.replace("{{LANG}}", lang_switch(code)).replace("{{HREFLANG}}", HREFLANG)
    assert "{{" not in out.replace("{{DEALERS}}", ""), "채워지지 않은 자리표시자가 있습니다"
    if code == "ko":
        return finish(out)
    tr = json.loads((ROOT / f"i18n/{code}.json").read_text(encoding="utf-8"))
    for ko, t in GEO_LABELS[code].items():
        out = out.replace(f"<th>{ko}</th>", f"<th>{t}</th>")
    out = translate(out, tr)
    m = tr["meta"]
    out = out.replace('<html lang="ko">', f'<html lang="{m["lang"]}">')
    out = out.replace(f'<link rel="canonical" href="{SITE}">', f'<link rel="canonical" href="{SITE}{m["path"]}">')
    out = out.replace(f'<meta property="og:url" content="{SITE}">', f'<meta property="og:url" content="{SITE}{m["path"]}">')
    out = out.replace('content="ko_KR"', f'content="{m["locale"]}"')
    out = out.replace('"inLanguage": "ko-KR"', f'"inLanguage": "{m["lang"]}"')
    out = re.sub(r"family=Archivo[^\"]*display=swap", m["fonts"], out, count=1)
    # 하위 폴더에서 이미지 경로
    out = re.sub(r'((?:src|href)=")images/', r"\1../images/", out)
    out = out.replace("url(images/", "url(../images/")
    left = sorted(set(re.findall(r"[^<>\"]*[가-힣][^<>\"]*", out)))
    left = [x.strip() for x in left if x.strip() and "/*" not in x]
    if left:
        print(f"[{code}] 번역되지 않은 한국어:", left[:20])
    return finish(out)


def main():
    manifest = (ROOT / ".github/image-manifest.txt").read_text().splitlines()
    cdn = dict(reversed(l.split()) for l in manifest if l.strip())
    for code, _, path in LANGS:
        out = render(code)
        used = set(re.findall(r"images/[\w/.-]+\.(?:jpg|png)", out))
        for u in sorted(used - set(cdn)):
            print("매니페스트에 없는 이미지:", u)
        if "--preview" in sys.argv:
            out = re.sub(r"(?:\.\./)?images/[\w/.-]+\.(?:jpg|png)", lambda m: cdn.get(m.group(0).replace("../", ""), m.group(0)), out)
            name = f"preview{'-' + code if code != 'ko' else ''}.html"
            (ROOT / name).write_text(out, encoding="utf-8")
            print(name)
        else:
            dest = ROOT / path / "index.html"
            dest.parent.mkdir(exist_ok=True)
            dest.write_text(out, encoding="utf-8")
            print(dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
