# tietoliikenteen_sovellusprojekti
Tietoliikenteen sovellusprojekti, mikä tehdään Severin kanssa.
<img width="1647" height="1214" alt="TL project architecture" src="https://github.com/user-attachments/assets/6fdc1994-5424-4b8d-a7a2-672b382fbf07" />

# Aloitus
Koko projektin ideana on se, että saadaan siirrettyä anturidataa mikrokontrollerilta MySql tietokantaan, joka toimii ubuntu serverillä. Mikrokontrollerin ja tietokannan välissä on Rasperry Pi-tietokone, joka vastaanottaa anturidatan mikrokontrollerilta käyttäen langatonta tiedonsiirto yhteyttä nimeltä Bluetooth Low Energy. Bluetooth Low Energy on IoT(Esineiden Internet) laitteille hyvin soveltuva tiedonsiirto protokolla, sillä se ei vie paljoa resursseja ja kuluttaa vähän virtaa. Rasperry Pi on yhdistettynä ethernet kaapelilla kytkimeen ja sitä kautta koulun sisäiseen tietoverkkoon. Sitä tietoverkkoa käyttäen se pystyy siirtämään dataa serverille, jossa tietokanta sijaitsee.
