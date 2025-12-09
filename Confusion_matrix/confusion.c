#include <zephyr/kernel.h>
#include <math.h>
#include <float.h>  // mahtuuko?
#include "confusion.h"
#include "adc.h"

#define READ_COUNT 100
#define READ_DELAY_MS 100
/* 
  K-means algorithm should provide 6 center points with
  3 values x,y,z. Let's test measurement system with known
  center points. I.e. x,y,z are supposed to have only values
  1 = down and 2 = up
  
  CP matrix is thus the 6 center points got from K-means algoritm
  teaching process. This should actually come from include file like
  #include "KmeansCenterPoints.h"
  
  And measurements matrix is just fake matrix for testing purpose
  actual measurements are taken from ADC when accelerator is connected.
*/

int CP[6][3] = {
    {1506, 1480, 1210}, // X_high
    {1519, 1505, 1810}, // X_low
    {1517, 1807, 1523},  // Y_high
    {1505, 1190, 1532},  // Y_low
    {1812, 1480, 1507}, // Z_high
    {1214, 1496, 1522}  // Z_low
};

int measurements[6][3]={
	                {1,0,0},
						 {2,0,0},
						 {0,1,0},
						 {0,2,0},
						 {0,0,1},
						 {0,0,2}
};

int CM[6][6]= {0};  // confusion matrix

int predicted = -1; // for debug print

void printConfusionMatrix(void)
{
   printk("ennustettu: %d \n", predicted); // debug printtaus, nähdään kuka voitti
	printk("Confusion matrix = \n");
	printk("    1   2   3   4   5   6\n");
	for(int i = 0;i<6;i++)
	{
		printk("cp%d %d   %d   %d   %d   %d   %d\n", i+1,CM[i][0], CM[i][1], CM[i][2], CM[i][3], CM[i][4], CM[i][5]); 
	}
}

void printConfusionMatrixCSV(void)
{
   printk("True predicted, 0,1,2,3,4,5\n");  // Otsikko

   // Käydään läpi confusion matrixin rivit
   for (int i = 0; i < 6; i++) {
      printk("%d", i);  // Tulostetaan oikea luokka (True class)

      // Tulostetaan jokainen ennustettu arvo (Predicted class)
      for (int j = 0; j < 6; j++) {
         // Tarkistetaan, ettei lisätä ylimääräisiä pilkkuja
         printk(",%d", CM[i][j]);  
      }
      printk("\n");  // Rivinvaihto seuraavalle riville
   }

   printk("   cp1 cp2 cp3 cp4 cp5 cp6\n");  // Otsikko, joka kertoo keskikohdat
}


void classifyRealSamples(int direction)
{
   if (direction <0 || direction >5) return;

   for (int i=0; i<READ_COUNT;i++) {
      struct Measurement m = readADCValue();
      printk("Measurement %d: x=%d y=%d z=%d\n", i+1, m.x, m.y, m.z); // debug printtaus
      predicted = calculateDistanceToAllCentrePointsAndSelectWinner(m.x, m.y, m.z, CP);
      if (predicted >=0 && predicted <6) {
         printk("Direction: %d Predicted: %d\n", direction, predicted); // debug printtaus
         CM[direction][predicted] += 1;
      }
      k_msleep(READ_DELAY_MS);
   }
}

void makeHundredFakeClassifications(void)
{
   /*******************************************
   Jos ja toivottavasti kun teet toteutuksen paloissa eli varmistat ensin,
   että etäisyyden laskenta 6 keskipisteeseen toimii ja osaat valita 6 etäisyydestä
   voittajaksi sen lyhyimmän etäisyyden, niin silloin voit käyttää tätä aliohjelmaa
   varmistaaksesi, että etäisuuden laskenta ja luokittelu toimii varmasti tunnetulla
   itse keksimälläsi sensoridatalla ja itse keksimilläsi keskipisteillä.
   *******************************************/
   printk("Make your own implementation for this function if you need this\n");
}

void makeOneClassificationAndUpdateConfusionMatrix(int direction)
{
   /**************************************
   Tee toteutus tälle ja voit tietysti muuttaa tämän aliohjelman sellaiseksi,
   että se tekee esim 100 kpl mittauksia tai sitten niin, että tätä funktiota
   kutsutaan 100 kertaa yhden mittauksen ja sen luokittelun tekemiseksi.
   **************************************/
   printk("Make your own implementation for this function if you need this\n");
}

// alkuperäinen versio
int calculateDistanceToAllCentrePointsAndSelectWinner(double x,double y,double z, int CP[6][3])
{
   /***************************************
   Tämän aliohjelma ottaa yhden kiihtyvyysanturin mittauksen x,y,z,
   laskee etäisyyden kaikkiin 6 K-means keskipisteisiin ja valitsee
   sen keskipisteen, jonka etäisyys mittaustulokseen on lyhyin.
   ***************************************/

   double bestDist = 1000000;
   int best = 0;

   for (int i = 0; i < 6; i++){
      double dx = x - CP[i][0]; 
      double dy = y - CP[i][1];
      double dz = z - CP[i][2];
      double dist = dx*dx + dy*dy + dz*dz; 
      
      printk("Distance to CP%d = %d\n", i+1, (int)dist); // debug printtaus, nähdään etäisyydet kaikkiin keskikohtiin

      if (dist < bestDist) {
         bestDist = dist;
         best = i;
      }
   }
   return best;
}

void resetConfusionMatrix(void)
{
	for(int i=0;i<6;i++)
	{ 
		for(int j = 0;j<6;j++)
		{
			CM[i][j]=0;
		}
	}
}

