# speedtest-multi
Uses the official speedtest CLI and implements multiple serial tests.

Python script to read the results from the CLI, and log them into a file. Will use multiple servers, in series, and also compile the best results.

I found that - in the version I tested - the JSON and text output differ, so I chose to capture the speedtest plain test output.

