# glucose2

This website allows me to track my daily blood glucose levels. My goal is to have a visual indicator of how various treatments affect my glucose. The chart's live beginnings, viewable at [wtrenker.com](https://wtrenker.com), shows the average daily blood glucose as a red line, it shows the target range by 2 solid horizontal lines, it shows the trend by a single dashed line (which is a 2nd degree polynomial curve fit), and it provides for notes on the chart to highlight key items.

A major feature is that the chart is generated in real-time so when I update the database daily I don't have to do anything to re-plot the chart. A very realistic example of the long term goal is documented on the live chart. It is the amazing improvement that Jardiance is making. I share this chart with my healthcare professionals who find it very helpful.

On the technical side, this is a Python, Sqlite, and Matplotlib project and is the 2nd major version of the glucose software, which involves a significant refactoring. This new version supports tracking the average daily blood glucose reading over a long time period, ultimately years, not just months.

I am using the open source [Caddy web server](https://caddyserver.com/) to front-end the web site. Caddy is a secure https server that uses commercial-grade open source security technology. It is a production server written in the [Go programming language](https://golang.org/) which features tighter security than many of it counterparts. I am also using this project to delve into the Go language which I feel is about to spring onto the web application development scene. As a Computer Scientist, working over the years in various computer languages, I think that the Go language brings together many of the advantageous features desired by the programming specialists in my profession.

-- William Trenker (wtrenker@gmail.com)
