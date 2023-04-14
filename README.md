# cs-market-utility
 ## Description
 The CS Market Utility is a set of utilities aimed at enhancing access to data pertaining to the Steam Marketplace economy, specific to CS:GO/CS2. I want to note that this does NOT (nor will it ever) automate market actions such as buying or selling, as this breaks Steam ToS and is also unethical in the first place.

## Requirements
* Python package requirements are given in requirements file
* Private Internet Access VPN (with desktop client and CLI)
* Access to /Items endpoint at https://steamapis.com/

## Setup
The main configuration for this script is handled in a .env file located in the base directory of the repository (same folder as the requirements file). If the file is malformed, or the script otherwise cannot get the data it needs from it the script will not execute.

There are currently two configurations that must be in this file:
1. **api_key**: This is your API key for SteamAPIs, needed to get certain market data.
2. **pia_loc**: The absolute path to your PIA application (i.e. C:/\<path>/piactl.exe). This is needed because the official PIA docs do not recommend adding this directory directly to your PATH, so in order to invoke the PIA CLI the script must reference the location of the executable when executing any PIA commands.

The above key-values must be structured in the order they are presented, with a colon separating the key and its associated value. (i.e. \<key>:\<value>). One item per line.


 ## Implemented Utilities
 * Price Change Checker
    * When this utility is run for the first time, a snapshot of current item prices are taken; on subsequent executions, the current item prices are compared to the most recent snapshot and any difference significant enough to at least breakeven given Steams 15% cut is displayed.

## Planned Utilities
* Historical Market Data
    * For a set of CS:GO items, get the historical price data (likely averaged month-to-month) and output to a tabular format.
* Investment Check
    * Given a list of skins and the price a user paid to receive them (or, what the skin was worth when the user traded for them), cross-reference with current market prices to determine investment ROI.
