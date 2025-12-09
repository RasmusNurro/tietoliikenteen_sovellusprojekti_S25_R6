/*
 * Copyright (c) 2020 Libre Solar Technologies GmbH
 *
 * SPDX-License-Identifier: Apache-2.0
 */
#include <zephyr/logging/log.h>
#include <dk_buttons_and_leds.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>
#include "adc.h"
#include <zephyr/device.h>
#include <zephyr/devicetree.h>

#include "confusion.h"



#define USER_LED1         	 	DK_LED1
#define USER_LED2          		DK_LED2
#define USER_LED3               DK_LED3
#define USER_LED4               DK_LED4

#define USER_BUTTON_1           DK_BTN1_MSK
#define USER_BUTTON_2           DK_BTN2_MSK
#define USER_BUTTON_3           DK_BTN3_MSK
#define USER_BUTTON_4           DK_BTN4_MSK

#define DEBUG 1  // 0 = changes direction when button 3 is pressed
                 // 1 = fake 100 measurements done to each 6 directions when 3 pressed.
static int direction = -1;	// 0 = x direction high
							// 1 = x directon low	
							// 2 = y direction high
							// 3 = y direction low
							// 4 = z direction high
							// 5 = z direction low

static const char *dirNames[6] = {
	"cp1-x high", "cp2-x low",
	"cp3-y high", "cp4-y low",
	"cp5-z high", "cp6-z low"
};                				 

LOG_MODULE_REGISTER(MAIN, LOG_LEVEL_INF);

static void button_changed(uint32_t state, uint32_t changed)
{
	if ((changed & USER_BUTTON_1) && (state & USER_BUTTON_1))
	{
		printk("Button 1 down, printing current Confusion Matrix and CM csv\n");
		printConfusionMatrix();
	}

	if ((changed & USER_BUTTON_2) && (state & USER_BUTTON_2)) 
	{
		printk("Button 2 down, resetting confusion matrix\n");
		resetConfusionMatrix();
		printConfusionMatrix();
	}		
	
	if ((changed & USER_BUTTON_3) && (state & USER_BUTTON_3)) 
	{
		direction++;
		if (direction >5) direction = 0;
		printk("Direction set to %s\n", dirNames[direction]);	
		
	}		

	if ((changed & USER_BUTTON_4) && (state & USER_BUTTON_4)) 
	{
		if (direction <0 ) {
			printk("Set direction first with button 3\n");
			return;
		}
		printk("Starting 100-sample classification for direction %s\n", dirNames[direction]);
		classifyRealSamples(direction);
		printConfusionMatrix();	
	}		
}


void main(void)
{
	initializeADC();
	resetConfusionMatrix();

	dk_leds_init();
	dk_buttons_init(button_changed);

	printk("Ready \n");
	printk("Button 1: Print confusion matrix\n");
	printk("Button 2: Reset confusion matrix\n");
	printk("Button 3: Change direction (current: none)\n");
	printk("Button 4: collect + classify 100 samples \n");

	while(1)
	{
		k_sleep(K_MSEC(1000));
		dk_set_led_on(USER_LED1);
		dk_set_led_on(USER_LED2);
		dk_set_led_on(USER_LED3);
		dk_set_led_on(USER_LED4);

		k_sleep(K_MSEC(1000));

		dk_set_led_off(USER_LED1);
		dk_set_led_off(USER_LED2);
		dk_set_led_off(USER_LED3);
		dk_set_led_off(USER_LED4);
	}
}


