# Crust Bikes Korea

crustbikes.co.kr 원페이지 정적 사이트 (GitHub Pages). parleecycles.co.kr, bastioncycles.co.kr, tsubasabicycles.co.kr과 같은 구조입니다.

- `index.html` 원페이지 본체 (CRUST · EVASION(+ TRAIL 140) · BOMBORA(+ CELOS) · STUPID TOURIST · PARTS · SHOWROOM)
- `index.src.html` 편집용 원본. 지오메트리 표는 `{{GEO_*}}` 자리에 `build.py`가 채웁니다. 표를 고치지 않을 때는 `index.html`을 직접 수정해도 됩니다.
- `build.py` 지오메트리 데이터와 빌드 스크립트. `python3 build.py`로 `index.html` 생성, `--preview`로 크러스트 CDN 이미지를 바로 쓰는 `preview.html` 생성
- `404.html` 하위 주소(/evasion, /bombora, /celos-bombora, /stupid-tourist, /dealer 등)를 섹션으로 연결
- `images/` 섹션별 이미지 (`hero`, `evasion`, `trail`, `bombora`, `celos`, `tourist`, `parts`)
- `.github/image-manifest.txt` + `fetch-images.yml` 크러스트 공식 사이트(crustbikes.com) CDN 이미지 이전용 워크플로

## 이미지
매니페스트를 수정해 main에 푸시하면 Actions가 이미지를 받아 `images/`에 커밋합니다.
이미 받은 파일은 건너뛰므로, 이미지를 교체할 때는 해당 파일을 지우거나 새 파일명으로 추가합니다.
첫 세팅 때는 Actions 탭에서 `Fetch images from Crust CDN`을 한 번 실행(Run workflow)하면 됩니다.

## 도메인
`CNAME`은 crustbikes.co.kr. 레지스트라 DNS에 GitHub Pages A 레코드 4개(185.199.108~111.153)와 `www` CNAME(sereno-kwon.github.io)을 연결합니다.
