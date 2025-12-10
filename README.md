# tietoliikenteen_sovellusprojekti
Tietoliikenteen sovellusprojekti ala Rasmus & Severi
<img width="647" height="414" alt="TL project architecture(1)" src="https://github.com/user-attachments/assets/35fde55a-0a42-44f0-8269-00d5c35ac53f" />

# Sisällysluettelo
- [Lähtökohta](#Lähtökohta)
- [Rasperry Pi:n valmistelu](#Rasperry-Pin-valmistelu)
- [Mikrokontrolleri](#Mikrokontrolleri)
- [Tietokanta palvelimella](#Tietokanta-palvelimella)
- [K-means ja Confusion Matrix](#K-means-ja-Confusion-Matrix)

# Lähtökohta
Lyhykäisyydessään koko projektin ideana on se, että saadaan siirrettyä anturidataa mikrokontrollerilta MySql tietokantaan ja sillä datalla koulutetaan koneoppimismalli. Mikrokontrollerin ja tietokannan välissä on Rasperry Pi-tietokone, joka vastaanottaa anturidatan mikrokontrollerilta käyttäen langatonta tiedonsiirto protokollaa nimeltä Bluetooth Low Energy. Bluetooth Low Energy on IoT(Esineiden Internet) laitteille hyvin soveltuva protokolla, sillä se ei vaadi paljoa resursseja ja kuluttaa vähän virtaa. Rasperry Pi on yhdistettynä ethernet kaapelilla kytkimeen ja sitä kautta koulun sisäiseen tietoverkkoon. Sitä tietoverkkoa käyttäen se pystyy siirtämään dataa Ubuntu serverille, jossa tietokanta sijaitsee. Lopuksi koulutetaan koneoppimismalli datalla, joka antureista saadaan. Projekti tehdään pareittain, mutta kuusi paria muodostaa yhden scrum ryhmän. Scrum ryhmä kokoontuu kerran viikossa ja käy läpi kaikkien projektin etenemisen ja ongelmatilanteet.

# Rasperry Pi:n valmistelu
Projekti aloitettiin valmistelemalla rasperry pi käyttöä varten. Siirsimme .img tiedoston muistikortille ja muistikortti asetettiin rasperryyn. Näin saimme asennettua käyttöjärjestelmän. Teimme myös tarvittavat konfiguroinnit SSH yhteyttä varten. Kytkimme ethernet kaapelilla rasperryn verkkoon, jonka jälkeen pääsemme SSH protokollaa käyttäen laitteeseen käsiksi omalta tietokoneelta. Näin pystymme asentamaan projektissa tarvittavia ohjelmia ja hallinnoimaan laitetta.
Kirjoitimme pythonilla ohjelman, joka käytti bleak kirjastoa yhdistääkseen Bluetooth Low Energyä käyttäen. Se yhdistää mikrokontrolleriin, joka toimii GATT palvelimena. Yhdistämistä varten tarvitaan mikrokontrollerin mac-osoite ja tietyn datan tilaamista varten sen UUID osoite. Rasperry pi toimii GATT asiakkaana, koska se tilaa mikrokontrollerilta UUID:n perusteella löytyvää dataa, eli x, y ja z data. Kehitysideana meidän koodiimme olisi se, että se yrittäisi yhdistää uudelleen, jos yhteys katkeaa. Tällä hetkellä uudelleenyhdistys vaatii ohjelman sulkemisen ja uudelleen käynnistämisen.

<img width="500" height="334" alt="Rasperry-tietokone_v3" src="https://github.com/user-attachments/assets/b4f02e45-41a4-4a82-8972-79ed45fcb3ed" />


# Mikrokontrolleri
Olennainen osa projektia on mikrokontrolleri, joka mittaa anturidataa ja lähettää Bluetooth LE:tä käyttäen. Projektissa käyttämämme mikrokontrolleri on Nordic Semiconductorin valmistama nRF5340dk. Mikrokontrolleri sopii projektiin täydellisesti sisäänrakennetun Bluetooth tuen takia ja pienen virrankulutuksensa vuoksi. Voidaksemme ohjelmoida kyseistä laitetta, täytyi meidän asentaa Visual Studio Code-sovellukseen tarvittavat lisäosat, kuten nRF Connect for VSCode, nRF Devicetree sekä tarvittavat sdk ja toolchain riippuvuudet. Lisäksi tietokoneelle piti asentaa Segger J-Link ohjelma, joka mahdollistaa mikrokontrollerin ohjelmoinnin USB-sarjaportin kautta. Flashasimme mikrokontrollerille pari ohjelmaa opettajan tunnilla ja muokkasimme valmista Bluetooth LE koodia meidän käyttöömme sopivaksi. Mittausdatan mittaa GY-61 niminen kiihtyvyysanturi, joka on kytkettynä mikrokontrollerin Vdd, gnd sekä kolmeen analog I/O porttiin. I/O porttien kautta anturi syöttää xyz dataa, joka on siis käytännössä jännitteen vaihtelu asennon vaihtumisen mukaan. Suunta muuttujaa saa vaihdettua painamalla nappia mikrokontrollerissa. Sen jälkeen ohjelma pakkaa x, y, z ja suunta datan pakettiin, joka lähetetään bluetoothin yli Rasperrylle.
Ohjelmamme siis asettaa mikrokontrollerin toimimaan GATT palvelimena, koska se lähettää asiakkaille niiden tilaamansa datan. Mikrokontrolleriin voi yhdistää kuka vaan, se ei ole suojattu esimerkiksi salasanalla.

<img width="343" height="273" alt="Näyttökuva 2025-12-10 115004" src="https://github.com/user-attachments/assets/4f70fc5d-6557-4199-aa1a-a0c0ce4212cc" />
Kiihtyvyysanturi.

<img width="476" height="236" alt="mikrokontrolleri_v2" src="https://github.com/user-attachments/assets/4627b3cb-311a-4697-843b-92ba2d168e01" />
Käytetty mikrokontrolleri.

# Tietokanta palvelimella
Tietokantamme sijaitsee Ubuntun virtuaalipalvelimella. Palvelimelle asensimme MySQL ohjelmiston ja loimme tietokannan. Sen jälkeen varmistimme pääsyn palvelimelle laitteille, jotka sitä tarvitsevat, kuten Rasperry Pi. Se vaati pienen määrän palomuuri konffausta, mutta sen kanssa ei ollut ongelmaa. Loimme käyttäjät MySQL ohjelmistoon, joilla on riittävät oikeudet tietokantaan datan lisäämiseksi ja hakemiseksi. Näitä käyttäjiä tarvitsi Rasperry Pi sekä tietokoneen python ohjelma, jolla data haettiin K-means algoritmia varten. Julkaisimme myös Apache/PHP nettisivun, jolta datan näkee verkkosivulla.

<img width="425" height="231" alt="Näyttökuva 2025-12-09 131930" src="https://github.com/user-attachments/assets/c3df15e7-3986-4842-93b0-2c567da8f0a7" />

# K-means ja Confusion Matrix
Teimme pienen python koodipätkän, jolla saimme haettua tietokannasta MySQL kyselyllä tarvittavat tiedot .csv tiedostoon. Siihen sisältyy x,y ja z data. Meillä on myös suunta data tietokannassa, mutta sitä ei k-means algoritmia varten tarvitse. Algoritmi siis laskee for loopissa centroidien paikat 3d tilassa. Laskenta perustuu centroidien etäisyyteen datapisteistä. Kun löytyy centroideille mahdollisimman pienet etäisyydet datapisteisiin kuin mahdollista, saavutetaan convergenssi, eli centroidit löytävät oman keskipisteensä. x, y ja z data muodostaa 6 datapisteiden kasaa, jotka luonnollisesti sitten vetävät centroidit niiden keskikohtaan. Centroidien xyz arvot sitten annetaan mikrokontrollerin ohjelmaan keskipisteet.h tiedostona. Keskipisteiden avulla confusion matrix ennustaa, mikä suunta on kyseessä.

<img width="930" height="794" alt="Näyttökuva 2025-12-09 093220" src="https://github.com/user-attachments/assets/f2d29873-bdee-4d62-a8ad-7005aa6793d7" />

Confusion matrixille annetaan suunta cp1-cp6 ja korreloiva suunta tulostuu ruudulle, jos suunta on oikea. Kuvassa mennään vuorotellen cp1 -> cp6 eli x oikeinpäin, x väärinpäin, y oikeinpäin, y väärinpäin yms. Eli kuvassa joka kohdassa confusion matrix ennustaa oikean suunnan centroidien perusteella.

<img width="316" height="181" alt="Näyttökuva 2025-12-09 092549" src="https://github.com/user-attachments/assets/a3d60b2c-03a8-4d0e-a895-ff50eb4f8bfa" />

