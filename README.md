# serterm
Simple Serial Terminal

## What?
A very simple Python implementation of a serial terminal. It sends and receives packages with a certain format:

## How?
usage: serterm.py [-h] port baudrate

Helper programm to talk to the smartlock dispatcher via serial

positional arguments:
  port        Serial Port
  baudrate    Baudrate

optional arguments:
  -h, --help  show this help message and exit

## Why?
Because I didn't like putty very much. And also because the recipient expects a certain header format.

## Dependencies?
- pyserial
