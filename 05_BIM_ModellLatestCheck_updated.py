import os
import re
import datetime

# Standard regexp-mönster för att matcha filnamn i 'Modell'-mappar
standard_mönster = re.compile(r"^[a-zA-Z]{2}[-_]\d{4}[-_]\d{4}V\d{3,5}[-_]\d{2}[-_]\d{2,3}\.dwg$", re.IGNORECASE)

# Särskilt mönster för DWG-filer i Station-mappar (ex: K593301-010-51-V001.dwg)
station_mönster = re.compile(r"^[A-Z]\d{6}-\d{3}-\d{2}-V\d{3}\.dwg$", re.IGNORECASE)

# Station-sökvägar (jämföras normaliserat/med små bokstäver)
station_sökvägar = [
    os.path.normcase(os.path.normpath(r"W:\\Projekt Urt-Hel\\Station")),
    os.path.normcase(os.path.normpath(r"W:\\Projekt Bfp-Urt\\Station")),
]


def hämta_gränsdatum():
    idag = datetime.datetime.now()
    return idag - datetime.timedelta(weeks=1)


def hitta_senaste_dwg_filer_i_modellmappar(rotmapp):
    resultat = []
    gränsdatum = hämta_gränsdatum()

    # Kontrollera om användaren angav en av station-sökvägarna
    norm_rot = os.path.normcase(os.path.normpath(rotmapp))
    är_station = norm_rot in station_sökvägar

    for mappnamn, undermappar, filnamn in os.walk(rotmapp):
        for fil in filnamn:
            if not fil.lower().endswith('.dwg'):
                continue

            sökväg = os.path.join(mappnamn, fil)
            # Välj mönster beroende på om det är en Station-mapp eller normalt 'Modell'-sök
            if är_station:
                matchar = station_mönster.fullmatch(fil)
            else:
                # För övriga sökvägar endast leta i mappar som heter 'Modell'
                if os.path.basename(mappnamn).lower() != 'modell':
                    continue
                matchar = standard_mönster.fullmatch(fil)

            if matchar:
                ändringsdatum = datetime.datetime.fromtimestamp(os.path.getmtime(sökväg))
                if ändringsdatum >= gränsdatum:
                    resultat.append((fil, ändringsdatum.strftime('%Y-%m-%d %H:%M:%S')))

    return sorted(resultat, key=lambda x: x[1], reverse=True)


def main():
    while True:
        rotmapp = input("\nAnge den fullständiga sökvägen till huvudmappen: ").strip('"')

        if not os.path.isdir(rotmapp):
            print("Ogiltig mappsökväg. Kontrollera och försök igen.")
        else:
            träffar = hitta_senaste_dwg_filer_i_modellmappar(rotmapp)
            print(träffar)

            if träffar:
                print("\nDWG-filer i 'Modell' eller Station-mappar är uppdaterade inom den senaste veckan:\n")
                for filnamn, datum in träffar:
                    print(f"{filnamn} - Senast ändrad: {datum}")
            else:
                print("Inga matchande DWG-filer hittades i de angivna mapparna den senaste veckan.")

        print("\nVad vill du göra nu?")
        print("1. Kör igen med en annan mapp")
        print("2. Avsluta")

        val = input("Ange ditt val (1 eller 2): ").strip()
        if val != '1':
            print("Avslutar...")
            break


if __name__ == "__main__":
    main()
