/*
 * Minimal xc.h compatibility header for transpilation
 * This is a mock version for testing - use real XC8 headers for production
 */

#ifndef _XC_H_
#define _XC_H_

// Basic PIC register definitions for common devices
#define _XTAL_FREQ 4000000  // Default crystal frequency

// Common PIC16 registers (example for PIC16F876A)
#ifndef PORTA
#define PORTA   (*(volatile unsigned char*)0x05)
#define PORTB   (*(volatile unsigned char*)0x06)
#define PORTC   (*(volatile unsigned char*)0x07)
#define TRISA   (*(volatile unsigned char*)0x85)
#define TRISB   (*(volatile unsigned char*)0x86)
#define TRISC   (*(volatile unsigned char*)0x87)
#endif

// Common bit manipulation macros
#ifndef _BV
#define _BV(bit) (1 << (bit))
#endif

// Delay functions (mock)
#define __delay_ms(x) /* delay implementation */
#define __delay_us(x) /* delay implementation */

// Configuration bits (example)
#ifndef __CONFIG
#define __CONFIG(x) /* configuration directive */
#endif

// Common data types (use compiler standard types when possible)
#ifndef uint8_t
typedef unsigned char uint8_t;
#endif
#ifndef uint16_t
typedef unsigned short uint16_t;
#endif
#ifndef uint32_t
typedef unsigned long uint32_t;
#endif

// PIC16F876A specific bit structures
struct {
    unsigned RA0:1;
    unsigned RA1:1;
    unsigned RA2:1;
    unsigned RA3:1;
    unsigned RA4:1;
    unsigned RA5:1;
    unsigned :2;
} PORTAbits;

struct {
    unsigned RC0:1;
    unsigned RC1:1;
    unsigned RC2:1;
    unsigned RC3:1;
    unsigned RC4:1;
    unsigned RC5:1;
    unsigned RC6:1;
    unsigned RC7:1;
} PORTCbits;

// Timer and interrupt control registers
unsigned char TMR0;
struct {
    unsigned T0IF:1;
    unsigned INTF:1;
    unsigned T0IE:1;
    unsigned INTE:1;
    unsigned RBIE:1;
    unsigned T0IE_:1;
    unsigned PEIE:1;
    unsigned GIE:1;
} INTCONbits;

struct {
    unsigned PS0:1;
    unsigned PS1:1;
    unsigned PS2:1;
    unsigned PSA:1;
    unsigned T0SE:1;
    unsigned T0CS:1;
    unsigned :2;
} OPTION_REGbits;

// EEPROM control registers
unsigned char EEDATA;
unsigned char EEADR;
unsigned char EECON1;
unsigned char EECON2;

// ADC control registers
unsigned char ADCON1;


struct {
    unsigned RD:1;
    unsigned WR:1;
    unsigned WREN:1;
    unsigned WRERR:1;
    unsigned :4;
} EECON1bits;

// Status register
struct {
    unsigned CARRY:1;
    unsigned DC:1;
    unsigned ZERO:1;
    unsigned PD:1;
    unsigned TO:1;
    unsigned RP0:1;
    unsigned RP1:1;
    unsigned IRP:1;
} STATUSbits;

#endif /* _XC_H_ */
