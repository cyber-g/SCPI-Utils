# SCPI-Utils
SCPI Utils is a personal collection of Linux tools, scripts, and reference material for working with SCPI-controlled instruments.

## Overview

This repository provides utilities for controlling and automating SCPI (Standard Commands for Programmable Instruments) compliant devices, with a focus on practical implementations for Linux environments.

## LXI-Tools Integration

[LXI-Tools](https://github.com/lxi-tools/lxi-tools) is a suite of command-line utilities for managing LXI (LAN eXtensions for Instrumentation) compliant instruments.

### Installation

On Debian-based systems:

```bash
sudo apt install lxi-tools
```

### Useful Commands

- Query instrument identification:
  ```bash
  lxi scpi --address <IP_ADDRESS> "*IDN?"
  ```

- Capture screenshot (for supported instruments only):
  ```bash
  lxi screenshot --address <IP_ADDRESS> --output screenshot.png
  ```

- Store screenshot to instrument memory (in general cases):
  ```bash
  lxi scpi --address <IP_ADDRESS> 'MMEM:STOR:IMAG "my.png"'
  ```

    This command saves a screenshot **to the instrument's internal memory**. 
    
    - You can then retrieve it using an appropriate file transfer method (e.g., FTP, HTTP).
    - or use an other SCPI command to transfer the file directly to your computer: 
    
        ```bash
        lxi scpi --address <IP_ADDRESS> 'MMEM:DATA? "my.png"'
        ```

    This command outputs the image data to the terminal as an IEEE-754 binary block transfer.  
    For parsing binary block data, see the included `get_screenshot.py` script or use libraries such as InstrumentKit's `binblockread` method: https://instrumentkit.readthedocs.io/en/latest/apiref/instrument.html#instruments.Instrument.binblockread.


## Specific instrument notes

### Keysight FieldFox Handheld Analyzers

The Keysight FieldFox series has limited support in LXI-Tools, necessitating custom scripts for full functionality.

The official programming guide is included for reference:  
[Keysight - FieldFox Handheld Analyzers - FFProgrammingHelp](Keysight/Keysight%20-%20FieldFox%20Handheld%20Analyzers%20-%20FFProgrammingHelp.pdf)  
*All rights reserved to Keysight. For personal use only. Do not distribute without permission.*

#### Sections worth to read:

##### Read Block Data using Csharp
The following example program illustrates how to parse block data using C#.
```csharp
/// <summary>
/// Generates a IEEE block header for the specified size.
/// </summary>
/// <remarks>
/// The block header is of the form #[digit indicating number of digits to follow][length]
/// e.g. 201 bytes -> "#3201
/// 9999 bytes -> "#49999"
/// 0 bytes -> "#10"
/// </remarks>
/// <param name="size">Size of the block.</param>
/// <returns>Block header size string.</returns>
string GenerateBlockHeader(int size)
{
 string sz = size.ToString();
 return "#" + sz.Length.ToString() + sz;
}
/// <summary>
/// Parses a partially digested IEEE block length header, and returns
/// the specified byte length.
/// </summary>
/// <remarks>
/// The Stream pointer is assumed to point to the 2nd character of the block header
/// (the first digit of the actual length). The caller is assumed to have parsed the
/// first two block header characters (#?, where ? is the number of digits to follow),
/// and converted the "number of digits to follow" into the int argument to this function.
/// </remarks>
/// <param name="numDigits">Number of digits to read from the stream that make up the
/// length in bytes.</param>
/// <returns>The length of the block.</returns>
int ReadLengthHeader(int numDigits)
{
 string bytes = string.Empty;
 for (int i = 0; i < numDigits; ++i)
 bytes = bytes + (char)Stream.ReadByte();
 return Convert.ToInt32(bytes);
} 
```

##### Transfer Image to PC

This example shows how to transfer an image (screenshot) on the FieldFox to a remote PC.

```scpi
# Store screen to my.png into the current directory on the FieldFox
# The default directory is the userdata directory on the instrument.
MMEM:STOR:IMAG "my.png"
# Transfers the contents of my.png as a BINBLOCK
# The file data that is returned by the 2nd command depends on the
programming environment.
# Environments like VEE, Matlab, C/VISA, etc. all deal with BINBLOCK
transfers in their own way.
MMEM:DATA? "my.png"
# Optionally delete of file from instrument's local storage
MMEM:DEL "my.png"
```

## Personal scripts

| Script | Description |
|--------|-------------|
| `get_screenshot.py` | Python script for capturing and downloading screenshots from SCPI instruments using socket connections, SCPI commands and BINBLOCK transfers. |

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

