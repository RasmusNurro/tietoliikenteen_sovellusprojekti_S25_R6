# tietoliikenteen_sovellusprojekti
Tietoliikenteen sovellusprojekti ala Rasmus & Severi
<img width="1647" height="1214" alt="TL project architecture" src="https://github.com/user-attachments/assets/6fdc1994-5424-4b8d-a7a2-672b382fbf07" />

# Lähtökohta
Lyhykäisyydessään koko projektin ideana on se, että saadaan siirrettyä anturidataa mikrokontrollerilta MySql tietokantaan ja sillä datalla koulutetaan koneoppimismalli. Mikrokontrollerin ja tietokannan välissä on Rasperry Pi-tietokone, joka vastaanottaa anturidatan mikrokontrollerilta käyttäen langatonta tiedonsiirto protokollaa nimeltä Bluetooth Low Energy. Bluetooth Low Energy on IoT(Esineiden Internet) laitteille hyvin soveltuva protokolla, sillä se ei vaadi paljoa resursseja ja kuluttaa vähän virtaa. Rasperry Pi on yhdistettynä ethernet kaapelilla kytkimeen ja sitä kautta koulun sisäiseen tietoverkkoon. Sitä tietoverkkoa käyttäen se pystyy siirtämään dataa Ubuntu serverille, jossa tietokanta sijaitsee. Lopuksi koulutetaan koneoppimismalli datalla, joka antureista saadaan. Projekti tehdään pareittain, mutta kuusi paria muodostaa yhden scrum ryhmän. Scrum ryhmä kokoontuu kerran viikossa ja käy läpi kaikkien projektin etenemisen ja ongelmatilanteet.

# Rasperry Pi:n valmistelu
Projekti aloitettiin valmistelemalla rasperry pi käyttöä varten. Siirsimme .img tiedoston muistikortille ja muistikortti asetettiin rasperryyn. Näin saimme asennettua käyttöjärjestelmän. Teimme myös tarvittavat konfiguroinnit SSH yhteyttä varten. Kytkimme ethernet kaapelilla rasperryn verkkoon, jonka jälkeen pääsemme SSH protokollaa käyttäen laitteeseen käsiksi omalta tietokoneelta. Näin pystymme asentamaan projektissa tarvittavia ohjelmia ja hallinnoimaan laitetta.

<img width="500" height="334" alt="Rasperry-tietokone_v3" src="https://github.com/user-attachments/assets/b4f02e45-41a4-4a82-8972-79ed45fcb3ed" />


# Mikrokontrolleri
Olennainen osa projektia on mikrokontrolleri, joka mittaa anturidataa ja lähettää Bluetooth LE:tä käyttäen. Projektissa käyttämämme mikrokontrolleri on Nordic Semiconductorin valmistama nRF5340. Mikrokontrolleri sopii projektiin täydellisesti sisäänrakennetun Bluetooth tuen takia ja pienen virrankulutuksensa vuoksi. Voidaksemme ohjelmoida kyseistä laitetta, täytyi meidän asentaa Visual Studio Code-sovellukseen tarvittavat lisäosat, kuten nRF Connect for VSCode sekä nRF Devicetree. Lisäksi tietokoneelle piti asentaa Segger J-Link ohjelma, joka mahdollistaa mikrokontrollerin ohjelmoinnin USB-sarjaportin kautta. Flashasimme mikrokontrollerille pari ohjelmaa opettajan tunnilla ja muokkasimme valmista Bluetooth LE koodia meidän käyttöömme sopivaksi.

<img width="476" height="236" alt="mikrokontrolleri_v2" src="https://github.com/user-attachments/assets/4627b3cb-311a-4697-843b-92ba2d168e01" />


# MySql
