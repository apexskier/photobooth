#!/bin/bash
kill -9 $(ps aux | grep PTPCamera | grep -v grep | tr -s ' ' | cut -d' ' -f2)