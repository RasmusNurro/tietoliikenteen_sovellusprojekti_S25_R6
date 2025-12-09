import numpy as np 
import matplotlib.pyplot as plt
from collections import Counter

# Määritellään CSV-tiedoston polku
csv_path = 'data_export.csv'

# Ladataan data CSV-tiedostosta käyttäen puolipistettä (;) erotinmerkkinä
# skip_header=1 ohittaa ensimmäisen rivin (otsikko), koska emme halua sitä dataksi
# dtype=float muuntaa kaikki arvot liukuluvuiksi (esim. 1200.0)
pts = np.genfromtxt(csv_path, delimiter=';', skip_header=1, dtype=float)

# Tarkistetaan, että tiedosto ei ole tyhjä
if pts.size == 0:  # Jos tiedostossa ei ole yhtään dataa, tulee virhe
    raise RuntimeError(f"Could not read {csv_path}")

X_data = pts[:, -3:].astype(float) # Otetaan kolme viimeistä saraketta (x, y, z -arvot) datasta
N = X_data.shape[0] # Lasketaan datapisteiden lukumäärä (kuinka monta riviä on datassa)
print(f"Ladattiin {N} data pistettä tiedostosta {csv_path}") # Tulostetaan, montako datapistettä onnistuttiin lataamaan

data = np.zeros((N, 4), dtype=float) # Luodaan uusi taulukko, jossa on 4 saraketta: x, y, z ja klusteritunniste (Alustus)
data[:, :3] = X_data # Kopioidaan x, y, z -arvot uuden taulukon kolmeen ensimmäiseen sarakkeeseen
data[:, 3] = -1 # Asetetaan klusteritunnisteiden paikka (sarake 4, indeksi 3) alkuarvoon -1, tähän säilytetään klusteritunnisteet myöhemmin

def kmeans(X, k, max_iters=100, tol=1e-4, n_init=10):
    # X: datapisteet (N x d taulukko, joss N on pisteiden määrä, d on dimensioiden määrä)
    # k: klusterien lukumäärä (kuinka monta ryhmää halutaan)
    # max_iters: enimmäismäärä iteraatioita (silmukan toistoja) ennen kuin pysäytetään
    # tol: konvergenssitoleranssi, eli millä tarkkuudella keskipisteiden on oltava vakaaa
    # n_init: kuinka monta eri alustusta ajetaan (valitaan paras SSE:n mukaan)

    n = X.shape     # Lasketaan datapisteiden lukumäärä (n)

    def kmeans_plus_plus_init(X, k, seed=None): # kmeans++ asettaa alkuclusterit paremmin, eli kauemmas toisistaan, ei tule virheitä
        # Luodaan satunnaislukugeneraattori, jonka siemen määritellään
        rng = np.random.RandomState(seed)
        
        # Lasketaan datapisteiden lukumäärä ja dimension
        n = X.shape[0]
        
        # Luodaan tyhjä taulukko, johon tallennetaan k clusterin keskipistettä
        centers = np.empty((k, X.shape[1]), dtype=float)
        i0 = rng.randint(n) # Valitaan satunnainen indeksi 0:sta n:ään
        centers[0] = X[i0] # Asetetaan ensimmäinen keskus tähän satunnaisesti valittuun pisteeseen

        # Lasketaan etäisyyden neliöt jokaisen pisteen ja ensimmäisen clusterin välillä
        # np.linalg.norm(...) laskee etäisyyden, ** 2 neliöi sen
        distances = np.linalg.norm(X - centers[0], axis=1) ** 2
        # Toistetaan loput k-1 clusteria
        for i in range(1, k):
            # Muutetaan etäisyyksien neliöt todennäköisyysjakaumaksi (normalisoidaan 0-1 välille)
            # Pisteet, jotka ovat kauempana, saavat suuremman todennäköisyyden
            probs = distances / distances.sum()
            # Valitaan uusi clusteri todennäköisyysjakauman mukaan
            # (kaukaiset pisteet valitaan todennäköisemmin)
            idx = rng.choice(n, p=probs)
            centers[i] = X[idx] # Asetetaan uusi clusteri valittuun pisteeseen
            new_dist = np.linalg.norm(X - centers[i], axis=1) ** 2 # Lasketaan etäisyyden neliöt uuden clusterin ja kaikkien pisteiden välillä
            distances = np.minimum(distances, new_dist) # Päivitetään etäisyydet: pidä pienemmät etäisyydet (lähimpään clusteriin)
        
        return centers # Palautetaan k aloitusclusteria
    # ei tarvitse käyttää tätä alustusta, on tarkka ilmankin.

    rng = np.random.RandomState(None) # Luodaan satunnaislukugeneraattori ilman siementä
    
    # Alustetaan parhaan tuloksen säilyttävät muuttujat
    best_sse = np.inf  # SSE = Sum of Squared Errors (virheiden neliöt yhteenlaskettu), aloitetaan äärettömyydestä
    best_labels = None  # Paras klusteritunnisteiden rivi (tyhjiä alussa)
    best_centroids = None  # Parhaat keskipisteet (tyhjiä alussa)
    
    # Toistetaan n_init kertaa eri alustuksilla
    for run in range(n_init):
        # Alustetaan keskipisteet k-means++ metodilla tai satunnaisesti
        # centroids =  kmeans_plus_plus_init(X, k, seed=rng.randint(1_000_000_000))
        idx = rng.choice(X.shape[0], size=k, replace=False)
        centroids = X[idx].astype(float).copy()
        labels = np.zeros(n, dtype=int) # Alustetaan klusteritunnisteet (aluksi kaikki 0)

        for it in range(max_iters): # Pääsilmukassa: Toista kunnes konvergenssi saavutetaan
            # Lasketaan etäisyydet kaikkien pisteiden ja kaikkien keskuksien välillä
            dist = np.linalg.norm(X[:, None, :] - centroids[None, :, :], axis=2) # axis = 2 = euklidinen etäisyys
            
            # Löydetään lähimpänä oleva keskus jokaiselle pisteelle
            # np.argmin(dist, axis=1) palauttaa indeksin (0-k) pienimmälle etäisyydelle
            new_labels = np.argmin(dist, axis=1) # axis = 1 = rivikohtainen minimi
            
            # Alustetaan uusien keskipisteiden taulukko (alussa nollia)
            new_centroids = np.zeros_like(centroids)
            
            # Käydään läpi jokainen klusteri (0:sta k:hon asti), päivitetään keskipisteet
            for j in range(k):
                pts = X[new_labels == j] # Valitaan kaikki pisteet, jotka kuuluvat klusteriin j
                # Jos klusterissa on vähintään yksi piste, lasketaan uusi keskus
                if pts.shape[0] > 0:
                    # Uusi keskus = kaikkien klusteriin kuuluvien pisteiden keskiarvo
                    new_centroids[j] = pts.mean(axis=0)
                else:
                    # Jos klusteri on tyhjä, etsi datapiste, joka on kauimpana omasta klusteristaan
                    # (tämä auttaa jakamaan suuren klusterin)
                    dists_to_assigned = np.linalg.norm(X - centroids[new_labels], axis=1)
                    # Etsi indeksi pisteen, joka on kauimpana (suurin etäisyys)
                    idx_farthest = int(np.argmax(dists_to_assigned))
                    # Aseta uusi keskus tälle kaukaiselle pisteelle
                    new_centroids[j] = X[idx_farthest].copy()
            
            # Lasketaan, kuinka paljon keskipisteet liikkuivat
            # (etäisyys vanhojen ja uusien keskipisteiden välillä)
            shift = np.linalg.norm(new_centroids - centroids)
            
            # Lasketaan, kuinka monta pistettä on jokaisessa klusterissa
            counts = np.bincount(new_labels, minlength=k)
            
            # Lasketaan nykyinen virhe (SSE) - kuinka hyvin datapisteet sopivat keskuksiin
            iter_sse = np.sum((X - new_centroids[new_labels]) ** 2) # virheiden neliöt yhteenlaskettu
            
            # Päivitetään keskipisteet ja tunnisteet uusiin arvoihin
            centroids = new_centroids
            labels = new_labels
            
            # Tulostetaan tiedot tästä iteraatiosta
            print(f"run {run} iter {it}: shift = {shift:.13f}, counts = {counts}, iter_SSE = {iter_sse:.3f}")
            
            # Jos shift on tarpeeksi pieni, konvergenssi on saavuteettu, voidaan lopettaa
            if shift < tol:
                break
        
        # Lasketaan lopullinen virhe tälle ajolle
        sse = np.sum((X - centroids[labels]) ** 2) # SSE = Sum of Squared Errors (virheet neliöinä)
        
        # Jos tämän ajon SSE on parempi (pienempi) kuin aiemmin paras, tallennetaan se
        if sse < best_sse:
            best_sse = sse  # Päivitetään paras SSE:n arvo
            best_labels = labels.copy()  # Tallennetaan parhaat klusteritunnisteet
            best_centroids = centroids.copy()  # Tallennetaan parhaat keskipisteet
        
    # Tulostetaan lopullisen valinnan SSE
    print(f"Selected best run SSE = {best_sse:.3f}")
    
    # Palautetaan paras löydetty ratkaisu (klusteritunnisteet ja keskipisteet)
    return best_labels, best_centroids

k = 6  # Datasetissä on 6 sensorin ryhmää: 6 clusteria
labels, centroids = kmeans(X_data, k) # Funktio palauttaa: labels (klusteritunnisteet) ja centroids (keskipisteet)

# Säilytetään klusteritunnisteet data-taulukkooon (neljäs sarake)
# Nyt jokainen datapiste tietää, mihin klusteriin se kuuluu
data[:, 3] = labels

# Tulostetaan k-meansin tulokset
# Tulostetaan, kuinka monta pistettä on kussakin klusterissa
print("K-means konvergoitui k =", k)
print("Klusterien laskenta:", dict(Counter(labels)))

# Tulostetaan löydetyt keskipisteet (klustereiden keskiarvot)
print("Keskipisteet:\n", centroids)

# Lasketaan klustereiden lukumäärä, joka on tottakai 6
k = centroids.shape[0]

# Avataan tiedosto 'keskipisteet.h' kirjoittamista varten
with open('keskipisteet.h', 'w', encoding='utf-8') as f:
    # Kirjoitetaan C-kielen taulukon alkua
    f.write(f"int CP[{k}][3] = {{\n")
    
    # Käydään läpi jokainen keskipiste
    for i, c in enumerate(centroids):
        # Tarkistetaan, onko keskipisteessä NaN-arvoja (ei-luku)
        # Jos on, korvataan ne nollalla
        c_clean = np.where(np.isnan(c[:3]), 0, c[:3])
        
        # Muutetaan koordinaatit kokonaisluvuiksi (pyöristetään lähimpään kokonaislukuun)
        vals = [int(round(float(v))) for v in c_clean]
        
        # Lisätään pilkku kaikkien paitsi viimeisen rivin jälkeen
        comma = "," if i < k - 1 else ""
        
        # Kirjoitetaan yksi klusterikeskus C-taulukkoon (muodossa {x, y, z})
        f.write(f"    {{{vals[0]}, {vals[1]}, {vals[2]}}}{comma}  // Keskipiste {i+1}\n")
    
    # Kirjoitetaan C-taulukon loppu
    f.write("};\n")

# Piirretään datapisteet 3D-kuvaajassa värikoodaamalla klusterit

# Luodaan uusi figuuripohja
fig = plt.figure(figsize=(8, 6))

# Luodaan 3D-akselit (joissa voidaan piirtää 3D-grafiikkaa)
ax = fig.add_subplot(111, projection='3d')

# Piirretään datapisteet väreillä koodattuina klusteritunnisteiden mukaan
# c=data[:,3] määrää värin klusteritunnisteiden mukaan
# cmap='viridis' on väripaletti (violetti -> keltainen)
# marker='o' tarkoittaa ympyrän muotoisia pisteitä
# s=20 määrää pisteiden koon
scatter = ax.scatter(data[:,0], data[:,1], data[:,2], c=data[:,3], cmap='viridis', marker='o', s=20)

# Piirretään löydetyt klustereiden keskipisteet punaisia X-merkkejä
# Nämä osoittavat kunkin klusterin "keskipisteen"
ax.scatter(centroids[:,0], centroids[:,1], centroids[:,2], c='red', marker='X', s=200, label='Keskipisteet')

# Nimetään akselit selvästi
ax.set_xlabel('X-akseli (sensorvalue_a)')  # Ensimmäisen sensori
ax.set_ylabel('Y-akseli (sensorvalue_b)')  # Toisen sensori
ax.set_zlabel('Z-akseli (sensorvalue_c)')  # Kolmannen sensori

# Lisätään legenda (selitys symboleista)
ax.legend()

# Näytetään grafiikka ekranolla (ikkunaan piirtyy kuva)
plt.show()
