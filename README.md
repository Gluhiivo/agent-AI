# Sales AI agent — lokalni RAG, M1

Prototip za pripravo prodajnega sestanka: lokalno poišče dokaze v dokumentih in sestavi odgovor z navedbami. Namenjen je enemu uporabniku na enem računalniku.

## Dejstva, predpostavke in odločitve

Pred začetkom razvoja je `main` vseboval samo `.gitkeep`, začetni commit `e55c420`, brez implementacije. Ta veja dodaja prvi prototip; ne pomeni, da so merila M1 že izpolnjena.

Predpostavke: majhen odobren korpus (~5 dokumentov), SLO/EN, en lokalni uporabnik. Strojna oprema, prava vsebina in zahtevana odzivnost še niso preverjeni.

Odločitve: Python 3.11+, CLI, lokalni Ollama, lokalni embeddingi, SQLite. SQLite nadomešča prvotno predlagani LanceDB: za majhen korpus omogoča trajni indeks brez dodatnih odvisnosti. Iskanje je polni pregled vektorjev s kosinusno podobnostjo; večji korpus bo zahteval drugo rešitev. Začetna kandidata modelov sta `bge-m3:latest` in `qwen3:4b`, ne potrjeni izbiri za vašo strojno opremo. Imena preverite v lokalnem Ollama; digest embedding modela se shrani v indeks.

## Podatkovni tok

Dokument → UTF-8 besedilo/PDF strani → odlomki → lokalni embeddingi → SQLite.
Vprašanje → lokalni embedding → top-k dokazi → lokalni LLM → preverjanje JSON in ID-jev navedb → odgovor ali zavrnitev.

Vektorji in besedilo so občutljivi podatki. Ni telemetrije aplikacije, oblačnega fallbacka, CRM integracij, pošiljanja sporočil ali orodij za izvajanje ukazov. Omrežna omejitev aplikacije sama ne omeji drugih procesov, vključno s strežnikom Ollama.

## Namestitev

Potrebujete Python 3.11 ali novejši in lokalno nameščen Ollama. Konkretna minimalna RAM/CPU konfiguracija ni potrjena. Med namestitvijo so lahko potrebni internetni prenosi. Med uporabo modelov aplikacija ne prenaša.

PowerShell iz korena repozitorija:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
# Samo če potrebujete PDF:
.\.venv\Scripts\python.exe -m pip install -r requirements-pdf.lock
Copy-Item config.example.toml config.toml
New-Item -ItemType Directory -Force data/input
Copy-Item tests/fixtures/offer.md data/input/
ollama pull bge-m3:latest
ollama pull qwen3:4b
ollama list
```

Na Linux/macOS uporabite `python3 -m venv .venv`, `.venv/bin/python -m pip install -e .`, `cp` in `mkdir -p`. Strežnik Ollama mora poslušati na `127.0.0.1:11434`; po potrebi ga zaženite z `ollama serve`. Uporabite le preverjene lokalne modele, brez posredovanja na cloud. Preverite licence prenesenih modelov.

`config.toml` uredite za svoje poti in lokalno nameščena imena modelov. Relativne poti se razrešijo glede na konfiguracijsko datoteko. Privzeti prag podobnosti 0.55 je začasen in ni dokaz zadostne kakovosti.

## Uporaba

```powershell
.\.venv\Scripts\python.exe -m sales_rag.cli ingest
.\.venv\Scripts\python.exe -m sales_rag.cli search "Koliko časa traja pilot?"
.\.venv\Scripts\python.exe -m sales_rag.cli ask
.\.venv\Scripts\python.exe -m sales_rag.cli reset --yes
```

`ask` brez argumenta vpraša za besedilo; s tem se vprašanje ne zapiše v zgodovino ukazov. Rezultat je JSON: posamezne trditve, ID-ji navedb ter izvorni odlomki z dokumentom in lokacijo. Terminal prikazuje občutljivo vsebino; ne delite izpisa ali preusmerjajte v javne dnevnike.

Podprti so UTF-8 TXT/Markdown in PDF z besedilom na vsaki strani (PDF zahteva dodatno odvisnost). OCR, šifrirani PDF, DOCX, PPTX in XLSX niso vključeni. Omejitev je 10 MiB na datoteko. Neznani formati, simbolne povezave in prevelike datoteke prekinejo uvoz.

`ingest` ponovno izdela celotni indeks in ga zamenja v transakciji šele po uspešni obdelavi. Tako ponoven uvoz ne podvaja odlomkov in odstrani dokumente, ki niso več v vhodni mapi. Ob napaki ostane prejšnji indeks. Prazen korpus ne izbriše indeksa: uporabite `reset --yes`.

`reset` odstrani indeksirane odlomke in metapodatke, izvirniki ostanejo. Ne zagotavlja odstranitve iz varnostnih kopij ali fizičnega izbrisa na SSD. Izvirnike, varnostne kopije in morebitne terminalske izpise odstranite ločeno.

## Varnost in omejitve

- Endpoint mora biti dobesedni `http://127.0.0.1:<port>`; proxyji in preusmeritve so onemogočeni. Drug lokalni proces lahko še vedno prestreže ali nadomesti strežnik.
- Zunanje povezave med uporabo blokirajte z OS požarnim zidom za aplikacijo in Ollama. Preizkusite `ingest` in `ask` po prenosu modelov s fizično odklopljenim omrežjem ter spremljajte poskuse povezav. To tukaj ni bilo izvedeno.
- Omejite pravice map na lokalnega uporabnika, omogočite zaščito diska in preverite sinhronizacijo map v oblak. Aplikacija sama ne šifrira podatkov in ne upravlja OS pravic.
- Vhodna mapa mora biti pod nadzorom istega uporabnika; ni utrjena pred sočasnim zlonamernim spreminjanjem datotek ali nevarnimi PDF-ji. Za nezaupanja vredne PDF-je uporabite izolirano okolje.
- Dokumenti so podatki, nikoli ukazi. Model ne dobi orodij. Prompt injection lahko kljub temu vpliva na odgovor; odpornost pravega modela ni dokazana.
- Preverjanje ID-jev virov ne preverja, ali trditev logično sledi iz vira. Ponudbe, cene in zaveze pred uporabo preveri človek. Prag iskanja ne zagotavlja pravilne zavrnitve.
- Ni avtentikacije ali ločevanja pravic med uporabniki. Prototip ni namenjen strežniški rabi.

## Testi in merila M1

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe eval/run.py --output eval/results-local.json
```

Za evalvacijo naj indeks vsebuje samo `tests/fixtures/offer.md`, ne injection dokumenta. Rezultati se shranijo lokalno in so izključeni iz Gita. Ocenjevalec ročno oceni pravilnost, podporo vsake trditve in ustrezno zavrnitev po `eval/README.md`.

M1 sprejem: vsaj 16/20 pravilnih, z dokazi podprtih odgovorov; zavrnitev vseh 5 vprašanj brez odgovora; veljavne in vsebinsko ustrezne navedbe; trajnost indeksa; brez dvojnikov; uspešen test blokiranega zunanjega prometa; adversarial test brez zunanjih dejanj; izmerjena odzivnost in poraba pomnilnika na ciljnem računalniku.

Začetno lokalno preverjanje: 16/16 sintetičnih testov na Python 3.12.14. Ti testi uporabljajo nadomestni model. Pravi modeli, kakovost SLO/EN, PDF dodatek, Windows, offline nadzor in strojna zmogljivost še niso preverjeni. GitHub Actions je konfiguriran za Windows/Linux in Python 3.11/3.12; rezultat preverite v PR.

## Razvoj

Glejte `AGENTS.md`, `docs/architecture.md`, `docs/security.md` in `docs/milestone.md`. Runtime za TXT/Markdown uporablja samo standardno knjižnico; `requirements-core.lock` je zato brez paketov. PDF dodatek je natančno pripet v `requirements-pdf.lock`. Build orodja in Ollama niso zaklenjeni: njihove dejansko uporabljene različice zabeležite ob sprejemnem preizkusu.
