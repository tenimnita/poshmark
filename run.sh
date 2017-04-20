#!/bin/bash
cd /home/ubuntu/ten/poshmark
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl poshmark
