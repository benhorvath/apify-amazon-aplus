# Apify Amazon A+ scraper

Amazon A+ is a feature for brand-registered sellers to create enhanced product listings with more engaging visuals, richer text, and interactive elements, replacing the standard product description to provide a better customer experience and potentially increase sales and brand trust.

This code creates an Apify actor that records the existence and quantity of these enhancements in product listings, as well as the standard product information. For example, the output marks if:

* Any A+ divs are present
* An A+ brand story hero image is present
* An A+ carousel carousel
* Etc.