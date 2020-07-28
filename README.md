# CharlieBoard

This is not an officially supported Google product.

This is not affiliated in any way with the Massachusetts Bay Transportation
Authority (MBTA).

## Overview

This is a departure board, as might be found in bus and train stations. It is
based around the MBTA, thus, "CharlieBoard". It was first used by loading it
onto a Raspberry Pi which was attached to a screen. As a result, the setup
assumes a single Web page being visible (`index.cgi`), with no user input. The
page refreshes once a minute to keep the bus times current.

This system uses the MBTA v3 API, documented at
https://www.mbta.com/developers/v3-api . It is a simple, REST-based JSON API.

For real usage, you should acquire an API key, however, the rates this board
work at are low enough that you don't need one while you are testing.

For convenience, I downloaded all routes and all stops into `routes.json` and
`stops.json`. `lookup-stop.sh` has an example of pulling one stop out by name,
so that you can access its ID for other API calls.

## Configuration

It's all coding, unfortunately.

This is hard-coded for a spot near Sullivan Station in Charlestown. Changes
require changes to the logic in `index.cgi`.

The main changes involve picking different stops. This was developed for a
location with two nearby stops, each with the same buses going in opposite
directions, with Sullivan Station as the nearest bus hub and so all buses in
this area are going towards or away from it. Other locations might have
different requirements. Look for calls to `get_stop()` to help guide your
changes.

## Usage

Arrange for `index.cgi` to be served from some URL. If it's all local on a
single device like a Raspberry Pi, then the URL doesn't even have to be globally
accessible, as long as the device has an Internet connection that can reach the
MBTA API. Put `index.template.html` and `predictions.template.html` in the same
working directory as `index.cgi`, and make `style.css` and `script.js` available
to the output of `index.cgi` (the simplest way, using Apache, is to put them all
in the same directory, and just make sure index.cgi is executed, not viewed
raw).

### Startup

If you want to make this have as little user interaction as possible, then
arrange for `index.cgi` to be displayed fullscreen as soon as the device boots.
This also means that if it ever gets stuck (occasionally errors seem to occur,
possibly related to the API, that the current exception handling can't recover
from), you can just power cycle the device.

On a Raspberry Pi, this can be accomplished by copying `autostart` into
`$HOME/.config/lxsession/LXDE-pi/autostart`, changing the URL as needed. The key
is to use --kiosk on chromium-browser, disabling user interface elements like
the "Restore pages?" popup.

### Usage

The MBTA doesn't run anything overnight, and there may be other times that
no-one could possibly see the screen so you would want to turn it off. For my
HDMI flatscreen, this command worked to turn the screen off:

$ vcgencmd display_power 0

And this turns it on again:

$ vcgencmd display_power 1

You might want to put these in a cron job.
